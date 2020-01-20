import sys
import os
import argparse
import signal
import time
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
            return "empty msg".encode()
        if msg[0] == "status":
            response = self.claudio_abbado.show_processes()
        elif msg[0] == "start":
            if msg[1] == "all":
                response = self.claudio_abbado.start_all_proc()
            else:
                for i in range(1, len(msg)):
                    reponse += self.claudio_abbado.start_proc(msg[i])
        elif msg[0] == "stop":
            if msg[1] == "all":
                response = self.claudio_abbado.stop_all_proc()
            else:
                for i in range(1, len(msg)):
                    reponse += self.claudio_abbado.stop_proc(msg[i])
        elif msg[0] == "restart":
            if msg[1] == "all":
                response = self.claudio_abbado.restart_all_proc()
            else:
                for i in range(1, len(msg)):
                    reponse += self.claudio_abbado.restart_proc(msg[i])
        elif msg[0] == "update":
            self.claudio_abbado.reload_conf(1, 1)
            response = "configuration reloaded"
        elif msg[0] == "pid":
            reponse = "taskmasterd pid is {}\n".format(self.claudio_abbado.pid)
        elif msg[0] == "shutdown":
            response = "taskmasterd pid {} quit\n".format(self.claudio_abbado.pid)
            stream.send(response.encode())
            self.quit()
        return response

    def run_server(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind(('', 5678))
        self.socket.listen(5)
        print('attend connexion')
        self.stream_client, info_client = self.socket.accept()
        print('connexion accept')
        msg = b''
        while msg != b'quit':
            msg = self.stream_client.recv(1024)
            response = self._handle_cmd(msg, self.stream_client)
            self.stream_client.send(response.encode())
        self.stream_client.close()
        self.socket.close()

def main(conf_file):
    supervisord = Supervisord(conf_file)
#    supervisord.run_supervisord()
    thread = threading.Thread(target=supervisord.run_supervisord, daemon=True)
    thread.start()
    supervisord.run_server()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("config_file", help="Please entre config file in yaml format")
    args = parser.parse_args()
    main(args.config_file)
