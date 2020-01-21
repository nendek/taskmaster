import sys
import os
import argparse
import signal
from process import Process
from orchestrator import Orchestrator
import threading
import socket
import logging
from logging.handlers import RotatingFileHandler
        
class Supervisord:
    def __init__(self, conf_file):
        self.init_logger()
        self.claudio_abbado = Orchestrator(conf_file, self.logger)
        self.socket = None
        self.stream_client = None
        signal.signal(signal.SIGTERM, self.quit)
        signal.signal(signal.SIGINT, self.quit)
        signal.signal(signal.SIGQUIT, self.quit)

    def init_logger(self):
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s :: %(levelname)s :: %(message)s')
        file_handler = RotatingFileHandler('taskmasterd.log', 'a', 1000000, 1)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

    def quit(self, sig, frame):
        self.logger.warning("taskmasterd received signal {}".format(sig))
        self.claudio_abbado.quit()
        if self.stream_client != None:
            self.stream_client.close()
        self.socket.close()
        del self.claudio_abbado
        sys.exit(0)

    def run_supervisord(self):
        while (1):
            self.claudio_abbado.update_processes()

    def _handle_cmd(self, msg, stream):
        response = ""
        msg = msg.decode()
        msg = msg.split()
        if len(msg) == 0:
            return "empty msg\n"
        if msg[0] == "status":
            response = self.claudio_abbado.show_processes()
        elif msg[0] == "start":
            if msg[1] == "all":
                response = self.claudio_abbado.start_all_proc()
            elif ":*" in msg[1]:
                group = msg[1].split(':')
                for prog in self.claudio_abbado.programs:
                    if prog.name_prog == group[0]:
                        response = prog.start_all()
                        break
                if response == "":
                    response = "{:30} group not exist\n".format(group[0])
            else:
                for i in range(1, len(msg)):
                    response += self.claudio_abbado.start_proc(msg[i])
        elif msg[0] == "stop":
            if msg[1] == "all":
                response = self.claudio_abbado.stop_all_proc()
            elif ":*" in msg[1]:
                group = msg[1].split(':')
                for prog in self.claudio_abbado.programs:
                    if prog.name_prog == group[0]:
                        response = prog.stop_all()
                        break
                if response == "":
                    response = "{:30} group not exist\n".format(group[0])
            else:
                for i in range(1, len(msg)):
                    response += self.claudio_abbado.stop_proc(msg[i])
        elif msg[0] == "restart":
            if msg[1] == "all":
                response = self.claudio_abbado.restart_all_proc()
            elif ":*" in msg[1]:
                group = msg[1].split(':')
                for prog in self.claudio_abbado.programs:
                    if prog.name_prog == group[0]:
                        response = prog.restart_all()
                        break
                if response == "":
                    response = "{:30}\tgroup not exist\n".format(group[0])
            else:
                for i in range(1, len(msg)):
                    response += self.claudio_abbado.restart_proc(msg[i])
        elif msg[0] == "update":
            self.claudio_abbado.reload_conf(1, 1)
            response = "configuration reloaded"
        elif msg[0] == "pid":
            response = "taskmasterd pid is {}\n".format(self.claudio_abbado.pid)
        elif msg[0] == "shutdown":
            self.quit(1,1)
        response = response[:-1]
        return response

    def _wait_connexion(self):
        self.logger.info('daemon waiting for client')
        self.stream_client, info_client = self.socket.accept()
        self.logger.info('client successfully connected to daemon')
        return self.stream_client

    def run_server(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.socket.bind(('', 5678))
        except Exception as e:
            self.logger.error("Error: {}".format(e))
            self.quit(1,1)
        self.socket.listen(5)
        self.stream_client = self._wait_connexion()
        msg = b''
        while msg != b'quit':
            msg = self.stream_client.recv(1024)
            if msg == b'':
                self.stream_client.close()
                self.logger.info("client disconnected")
                self.stream_client = self._wait_connexion()
            response = self._handle_cmd(msg, self.stream_client)
            try:
                self.stream_client.send(response.encode())
            except Exception as e:
                self.logger.error("Error: {}".format(e))
                self.quit(1,1)
        self.stream_client.close()
        self.socket.close()

def main(conf_file):
    supervisord = Supervisord(conf_file)
    thread = threading.Thread(target=supervisord.run_supervisord, daemon=True)
    thread.start()
    supervisord.run_server()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("config_file", help="Please entre config file in yaml format")
    args = parser.parse_args()
    main(args.config_file)
