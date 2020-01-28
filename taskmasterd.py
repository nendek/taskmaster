#!/bin/python3
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
            self.logger.error(e.__str__())
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
            "start": self.action,
            "stop": self.action,
            "restart": self.action,
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
        self.claudio_abbado.quit_orchestrator()
        if self.stream_client != None:
            self.stream_client.close()
        self.socket.close()
        del self.claudio_abbado
        sys.exit(0)

    def run_supervisord(self):
        while (1):
            self.claudio_abbado.update_processes()

    def get_response(self, cmd):
        cmd = cmd.split()
        if len(cmd) == 0:
            self.stream_client = self._wait_connexion()
            return ""
        elif len(cmd) == 1:
            response = self.dic_fcts[cmd[0]]()
        else:
            response = self.dic_fcts[cmd[0]](cmd)
        return response

    def status(self):
        response = self.claudio_abbado.status()
        return response

    def update(self):
        reponse = self.reload_conf(0, 0)
        return "configuration reloaded\n"
    
    def pid(self):
        return "taskmasterd pid is {}\n".format(os.getpid())
    
    def shutdown(self):
        self.quit()

    def restart(self, msg):
        pass

    def action(self, msg):
        status = ["ERROR (no such process)", "", "ERROR (already {})"]
        if msg[0] == "restart":
            msg[0] = "stop"
            response = self.action(msg)
            msg[0] = "start"
            response += self.action(msg)
            return response
        elif msg[0] == "start":
            fct = self.claudio_abbado.start
            action = "started"
        elif msg[0] == "stop":
            fct = self.claudio_abbado.stop
            action = "stopped"
        status[1] += action
        status[2] = status[2].format(action)
        response = ""
        if "all" in msg:
            for program in self.claudio_abbado.programs:
                for process in program.process:
                    ret = fct(process.name_proc)
                    response += "{}: {}\n".format(process.name_proc, status[ret])
            return response
        else:
            for i in range(1, len(msg)):
                if ":*" in msg[i]:
                    group = msg[i].split(":*")
                    for program in self.claudio_abbado.programs:
                        if program.name_prog == group[0]:
                            for process in program.process:
                                ret = fct(process.name_proc)
                                response += "{}: {}\n".format(process.name_proc, status[ret])
                            return response
                    response += "{}: ERROR (no such group)\n".format(group[0])
                else:
                    ret = fct(msg[i])
                    response += "{}: {}\n".format(msg[i], status[ret])
            return response

    def reload_conf(self, sig, stack):
        try:
            self.config_parser.parse_config()
            self.claudio_abbado.update(self.config_parser.configs)
        except ParsingError as e:
            self.logger.error(e.__str__())
            self.quit()
        
    def _wait_connexion(self):
        self.logger.info('daemon waiting for client')
        self.stream_client, info_client = self.socket.accept()
        self.logger.info('client successfully connected to daemon')
        return self.stream_client

    def start_server(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            self.socket.bind(('', 5678))
            self.socket.listen(0)
        except Exception as e:
            self.logger.error("Error: {}".format(e))
            self.quit()
            
    def read_from_client(self):
        msg = self.stream_client.recv(1024).decode()
        self.logger.info("received request: {}".format(msg))
        return msg

    def send_to_client(self, msg):
        msg += "##arpn"
        self.stream_client.send(msg.encode())
        
    def run_server(self):
        self.stream_client = self._wait_connexion()
        while True:
            try:
                request = self.read_from_client()
                response = self.get_response(request)
                self.send_to_client(response)
            except Exception as e:
                self.logger.error(e.__str__())
                self.quit()

def main(conf_file):
    supervisord = Supervisord(conf_file)
    supervisord.start_server()
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
            supervisord.claudio_abbado.start_orchestrator()
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
