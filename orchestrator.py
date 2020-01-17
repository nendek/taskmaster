import yaml
import time
import signal
import os
from program import Program

class Orchestrator():
    def __init__(self, config_file_name):
        self.path = os.path.join(os.path.abspath(os.path.dirname(config_file_name)), config_file_name)
        self.configs = {}
        self.programs = self.start()
        signal.signal(signal.SIGHUP, self.reload_conf)

    def start(self):
        data = self.get_config_file()
        self.configs = {"programs": {}}
        progs = []
        for elem in data["programs"]:
            self.configs["programs"][elem] = self.clean_config(data["programs"][elem])
            progs.append(Program(self.configs["programs"][elem], elem))
        return progs

    def update_processes(self):
        """
        this function is aimed to update processes informations 
        and relaunch stopped processes when it's needed 
        """
        for program in self.programs:
            for process in program.process:
                process.update_status()
                if process.status == "BACKOFF":
                    process.start(program.data)
                if program.autorestart == True:
                    if process.status == "EXITED":
                        process.start(program.data)
                if program.autorestart == "unexpeced":
                    if process.status == "EXITED":
                        if process.return_code not in program.exitcodes:
                            process.start(program.data)

    def show_processes(self):
        self.update_processes()
        for program in self.programs:
            for process in program.process:
                print("nom du programme: {}".format(process.name_proc))
                print(process)
            print("")

    def get_config_file(self):
        with open(self.path) as f:
            try:
                data = yaml.safe_load(f)
                if not "programs" in data.keys():
                    raise NameError("NO_PROG")
                for elem in data["programs"]:
                    if not "cmd" in data["programs"][elem]:
                        raise NameError("NO_CMD")
            except yaml.YAMLError as e:
                print("YAML file format error:")
                print(e)
            except NameError as e:
                if e.__str__() == "NO_CMD":
                    print("No cmd in config file")
                elif e.__str__() == "NO_PROG":
                    print("No programs in config file")
                else:
                    raise e
        return data
        

    def clean_config(self, data):
        config = {}
        config["cmd"] = data["cmd"]
        if "numprocs" in data.keys():
            config["numprocs"] = data["numprocs"]
        else:
            config["numprocs"] = 1

        if "umask" in data.keys():
            config["umask"] = data["umask"]
        else:
            config["umask"] = "022"

        if "working_dir" in data.keys():
            config["working_dir"] = data["working_dir"]
        else:
            config["working_dir"] = "."

        if "autostart" in data.keys():
            config["autostart"] = data["autostart"]
        else:
            config["autostart"] = True

        if "autorestart" in data.keys():
            config["autorestart"] = data["autorestart"]
        else:
            config["autorestart"] = "unexepected"

        if "startretries" in data.keys():
            config["startretries"] = data["startretries"]
        else:
            config["startretries"] = 3

        if "starttime" in data.keys():
            config["starttime"] = data["starttime"]
        else:
            config["starttime"] = 1

        if "stopsignal" in data.keys():
            sig_conf = data["stopsignal"]
            if sig_conf == signal.SIGTERM.name:
                config["stopsignal"] = signal.SIGTERM
            elif sig_conf == signal.SIGINT.name:
                config["stopsignal"] = signal.SIGINT
            elif sig_conf == signal.SIGQUIT.name:
                config["stopsignal"] = signal.SIGQUIT
            elif sig_conf == signal.SIGHUP.name:
                config["stopsignal"] = signal.SIGHUP
            elif sig_conf == signal.SIGKILL.name:
                config["stopsignal"] = signal.SIGKILL
            elif sig_conf == signal.SIGUSR1.name:
                config["stopsignal"] = signal.SIGUSR1
            elif sig_conf == signal.SIGUSR2.name:
                config["stopsignal"] = signal.SIGUSR2
            else:
                #log pas le bon signal de stop
                config["stopsignal"] = signal.SIGTERM
        else:
            config["stopsignal"] = signal.SIGTERM

        if "stoptime" in data.keys():
            config["stoptime"] = data["stoptime"]
        else:
            config["stoptime"] = 10

        if "stdout" in data.keys():
            config["stdout"] = data["stdout"]
        else:
            config["stdout"] = False

        if "stderr" in data.keys():
            config["stderr"] = data["stderr"]
        else:
            config["stderr"] = False

        if "exitcodes" in data.keys():
            config["exitcodes"] = []
            if type(data["exitcodes"]) == int:
                config["exitcodes"].append(data["exitcodes"])
            else:
                for elem in data["exitcodes"]:
                    config["exitcodes"].append(elem)
        else:
            config["exitcodes"] = [0]

        if "env" in data.keys():
            config["var_env"] = data["env"].copy()
        else:
            config["var_env"] = {}

        return config

    def reload_conf(self, signum, stack):
        pass
#        data = self.get_config_file()
#        progs = []
#        for program in self.programs:
#            if program.name_prog not in data["programs"]:
#                del program
#            elif self._same_configs(program.config, data["programs"][program.name_prog]) == False:
#                progs.append(Program(data["programs"][program.name_prog], program.name_prog, start=False))
#                del program



    def _same_configs(self, dic1, dic2):
        return True

    def start_proc(self, name):
        for program in self.programs:
            if program.start(name):
                return
        print("name error")
        return
    
    def start_all_proc(self):
        for program in self.programs:
            program.start_all()
        return

    def kill_all_proc(self):
        for program in self.programs:
            program.kill_all()

    def kill_proc(self, name):
        for program in self.programs:
            if program.kill(name):
                return
        print("name error")
        return
    
    def stop_all_proc(self):
        for program in self.programs:
            program.stop_all()

    def stop_proc(self, name):
        for program in self.programs:
            if program.stop(name):
                return
        print("name error")
        return
    
    def restart_proc(self, name):
        for program in self.programs:
            if program.restart(name):
                return
        print("name error")
        return
    
    def restart_all_proc(self):
        for program in self.programs:
            program.restart_all()
        return
