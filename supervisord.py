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
            print(msg)
            stream_client.send(b'nude')
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
