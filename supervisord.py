import sys
import os
import argparse
import signal
import time
from process import Process
from orchestrator import Orchestrator
        
class Supervisord:
    def __init__(self, conf_file):
        self.claudio_abbado = Orchestrator(conf_file)
        signal.signal(signal.SIGTERM, self.quit)
        signal.signal(signal.SIGINT, self.quit)
        signal.signal(signal.SIGQUIT, self.quit)

    def quit(self):
        del self.claudio_abbado
        sys.exit(0)

    def run(self):
        self.claudio_abbado.show_processes()
        while (1):
            self.claudio_abbado.update_processes()

def main(conf_file):
    supervisord = Supervisord(conf_file)
    supervisord.run()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("config_file", help="Please entre config file in yaml format")
    args = parser.parse_args()
    main(args.config_file)
