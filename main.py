import sys
import os
import yaml
import argparse
import signal
import time
from program import Program
from process import Process



def parse_cmd(l):
    print(l, end = '')
    if l == "exit":
        exit()

def parse_config_file(conf_file):
    with open(conf_file) as f:
        try:
            progs = []
            data = yaml.safe_load(f)
            if not "programs" in data.keys():
                raise NameError("NO_PROG")
            for elem in data["programs"]:
                if not "cmd" in data["programs"][elem]:
                    raise NameError("NO_CMD")
            for elem in data["programs"]:
                progs.append(Program(data["programs"][elem], elem))

        except yaml.YAMLError as e:
            print("YAML file format error:")
            print(e)
        except NameError as e:
            if e.__str__() == "NO_CMD":
                print("No cmd in config file")
            elif e.__str__() == "NO_PROG":
                print("No programs in config file")

        process = progs[0].process[0]
        print(progs[0])
        print(process)
        time.sleep(3)
        process.update_child_status()
        print(process)


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
    parse_config_file(conf_file)
    #for l in sys.stdin:
    #    parse_cmd(l)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("config_file", help="Please entre config file in yaml format")
    args = parser.parse_args()
    main(args.config_file)
