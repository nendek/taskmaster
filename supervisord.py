import sys
import os
import argparse
import signal
from process import Process
from orchestrator import Orchestrator
import threading
import socket
        
class Supervisord:
    def __init__(self, conf_file):
        self.claudio_abbado = Orchestrator(conf_file)
        signal.signal(signal.SIGTERM, self.quit)
        signal.signal(signal.SIGINT, self.quit)
        signal.signal(signal.SIGQUIT, self.quit)

    def quit(self, sig, frame):
        self.claudio_abbado.quit()
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
            response = "taskmasterd pid {} shutdown\n".format(self.claudio_abbado.pid)
            response = response[:-1]
            stream.send(response.encode())
            self.quit(1,1)
        response = response[:-1]
        return response

    def _wait_connexion(self):
        print('attend connexion')
        stream_client, info_client = self.socket.accept()
        print('connexion accept')
        return stream_client

    def run_server(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.socket.bind(('', 5678))
        except Exception as e:
            print("Error: {}".format(e))
            self.quit(1,1)
        self.socket.listen(5)
        stream_client = self._wait_connexion()
        msg = b''
        while msg != b'quit':
            msg = stream_client.recv(1024)
            if msg == b'':
                stream_client.close()
                stream_client = self._wait_connexion()
            response = self._handle_cmd(msg, stream_client)
            try:
                stream_client.send(response.encode())
            except Exception as e:
                print("Error: {}".format(e))
                self.quit(1,1)
        stream_client.close()
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
