import sys
import os
import argparse
import signal
import time
from process import Process
from orchestrator import Orchestrator



def parse_cmd(l):
    print(l, end = '')
    if l == "exit":
        exit()

#        process = progs[0].process[0]
#        print(progs[0])
#        print(process)
#        time.sleep(3)
#        process.update_child_status()
#        print(process)


#            process.start()
#            for proc in procs:
#                print(proc)
#                print('\n')

#            print("creation d'un process:")
#            ex = Process()
#            print(ex)
#            print()
#            print("start d'un process:")
#            ex.start()
#            print(ex)
#            print()
#            print("restart d'un process:")
#            ex.restart(signal.SIGKILL)
#            print(ex)
#            print()
#            print("stop d'un process:")
#            ex.stop(signal.SIGKILL)
#            print(ex)
#            print()



def main(conf_file):
    claudio_abbado = Orchestrator(conf_file)
    claudio_abbado.show_processes()
#    claudio_abbado.reload_conf(1, 1)
#    for i in range(0, 6):
#        time.sleep(0.4)
#        print("\n\n\n")
#        claudio_abbado.show_processes()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("config_file", help="Please entre config file in yaml format")
    args = parser.parse_args()
    main(args.config_file)
