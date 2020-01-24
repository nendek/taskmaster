import sys
import os
import argparse
import signal
from process import Process
from orchestrator import Orchestrator
from config_handler import Config_parser, ParsingError
import threading
import socket
import logging
from logging.handlers import RotatingFileHandler
        
class Supervisord:
    def __init__(self, conf_file):
        self.init_logger()
        try:
            self.config_parser = Config_parser(conf_file)
            self.config_parser.parse_config()
        except ParsingError as e:
            self.logger.Error(e.__str__())
            print(e)
            sys.exit()
        self.claudio_abbado = Orchestrator(self.config_parser.configs, self.logger)
        self.socket = None
        self.stream_client = None
        signal.signal(signal.SIGTERM, self.quit)
        signal.signal(signal.SIGINT, self.quit)
        signal.signal(signal.SIGQUIT, self.quit)
        signal.signal(signal.SIGHUP, self.reload_conf)
        self.dic_fcts = {
            "status": self.status,
            "start": self.multiple_arg,
            "stop": self.multiple_arg,
            "restart": self.multiple_arg,
            "update": self.update,
            "pid": self.pid,
            "shutdown": self.shutdown
        }

    def init_logger(self):
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s :: %(levelname)s :: %(message)s')
        file_handler = RotatingFileHandler('taskmasterd.log', 'a', 1000000, 1)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

    def quit(self, sig="shutdown", frame=None):
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

    def status(self):
        response = self.claudio_abbado.show_processes()
        return response

    def update(self):
        reponse = self.reload_conf(0, 0)
        return "configuration reloaded"
    
    def pid(self):
        return "taskmasterd pid is {}".format(os.getpid())
    
    def shutdown(self):
        self.quit()

    def multiple_arg(self, msg):
        if msg[0] == "start":
            fct = claudio_abbado.start_proc()
        elif msg[0] == "stop":
            fct = claudio_abbado.stop_proc()
        elif msg[0] == "restart":
            fct == claudio_abbado.restart_proc()

        if msg[1] == "all":
            for program in self.claudio_abbado.programs:
                for process in program.process:
                    process.start(process.data)

    def _handle_cmd(self, msg, stream):
        response = ""
        msg = msg.decode()
        msg = msg.split()
        if len(msg) == 0:
            return "empty msg"
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
                    response = "{:30} group not exist".format(group[0])
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
                    response = "{:30} group not exist".format(group[0])
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
                    response = "{:30}\tgroup not exist".format(group[0])
            else:
                for i in range(1, len(msg)):
                    response += self.claudio_abbado.restart_proc(msg[i])
        elif msg[0] == "update":
            self.reload_conf(0, 0)
            response = "configuration reloaded"
        elif msg[0] == "pid":
            response = "taskmasterd pid is {}".format(os.getpid())
        elif msg[0] == "shutdown":
            self.shutdown()
        return response

    def reload_conf(self, sig, stack):
        try:
            self.config_parser.parse_config()
            self.claudio_abbado.reload_conf(self.config_parser.configs)
        except ParsingError as e:
            self.logger.error(e.__str__())
            self.quit()
        
    def _wait_connexion(self):
        self.logger.info('daemon waiting for client')
        self.stream_client, info_client = self.socket.accept()
        self.logger.info('client successfully connected to daemon')
        return self.stream_client

    def run_server(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            self.socket.bind(('', 5678))
        except Exception as e:
            self.logger.error("Error: {}".format(e))
            self.quit()
        self.socket.listen(0)
        self.stream_client = self._wait_connexion()
        msg = b''
        while msg != b'quit':
            msg = self.stream_client.recv(1024)
            if msg == b'':
                self.stream_client.close()
                self.logger.info("client disconnected")
                self.stream_client = self._wait_connexion()
                continue
            response = self._handle_cmd(msg, self.stream_client)
            try:
                self.stream_client.send(response.encode())
            except Exception as e:
                self.logger.error("Error: {}".format(e))
                self.quit()
        self.stream_client.close()
        self.socket.close()

def main(conf_file):
    supervisord = Supervisord(conf_file)
    try:
        pid = os.fork()
    except Exception as e:
        print("Error fork: {}".format(e))
        return
    if pid == 0:
        signal.signal(signal.SIGQUIT, signal.SIG_IGN)
        signal.signal(signal.SIGINT, signal.SIG_IGN)
        signal.signal(signal.SIGTSTP, signal.SIG_IGN)
        signal.signal(signal.SIGCONT, signal.SIG_IGN)
        signal.signal(signal.SIGTTIN, signal.SIG_IGN)
        signal.signal(signal.SIGTTOU, signal.SIG_IGN)
        signal.signal(signal.SIGCHLD, signal.SIG_DFL)
        try:
            os.setsid()
        except Exception as e:
            print("Error setsid: {}".format(e))
            return
        try:
            pid = os.fork()
        except Exception as e:
            print("Error fork: {}".format(e))
            return
        if pid == 0:
            supervisord.claudio_abbado.start()
            thread = threading.Thread(target=supervisord.run_supervisord, daemon=True)
            thread.start()
            supervisord.run_server()
        else:
            return
    else:
        return

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("config_file", help="Please entre config file in yaml format")
    args = parser.parse_args()
    main(args.config_file)
