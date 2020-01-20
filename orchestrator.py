import yaml
import time
import signal
import os
import sys
from program import Program

class Orchestrator():
    def __init__(self, config_file_name):
        self.path = os.path.join(os.path.abspath(os.path.dirname(config_file_name)), config_file_name)
        self.configs = {}
        self.configs = self._get_configs()
        self.programs = self.start()
        signal.signal(signal.SIGHUP, self._reload_conf)

    def start(self):
        progs = []
        for elem in self.configs["programs"]:
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
                if program.autorestart == "unexpected":
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

    def _get_configs(self):
        configs = {"programs": {}}
        data = self._get_config_file()
        for elem in data["programs"]:
            configs["programs"][elem] = self._clean_config(data["programs"][elem])
        return configs

    def _get_config_file(self):
        with open(self.path) as f:
            try:
                data = yaml.safe_load(f)
                self._parsing_yaml(data)
            except yaml.YAMLError as e:
                print("YAML file format error:")
                print(e)
        return data
    
    def _parsing_yaml(self, data):
        try:
            if not "programs" in data.keys():
                raise NameError("NO_PROG")
            for elem in data["programs"]:
                #cmd
                if not "cmd" in data["programs"][elem]:
                    raise NameError("NO_CMD")
                elif type(data["programs"][elem]["cmd"]) != str:
                    raise NameError("BAD_CMD")
                #numprocs
                if "numprocs" in data["programs"][elem]:
                    if type(data["programs"][elem]["numprocs"]) != int:
                        raise NameError("BAD_NP")
                #umask
                if "umask" in data["programs"][elem]:
                    if type(data["programs"][elem]["umask"]) != int:
                        raise NameError("BAD_UM")
                #working_dir
                if "working_dir" in data["programs"][elem]:
                    if type(data["programs"][elem]["working_dir"]) != str:
                        raise NameError("BAD_WD")
                    if not os.path.exists(data["programs"][elem]["working_dir"]) or not\
                            os.path.isdir(data["programs"][elem]["working_dir"]):
                                raise NameError("BAD_WD")
                #autostart
                if "autostart" in data["programs"][elem]:
                    if type(data["programs"][elem]["autostart"]) != bool:
                        raise NameError("BAD_AS")
                #autorestart
                if "autorestart" in data["programs"][elem]:
                    if type(data["programs"][elem]["autorestart"]) == str:
                            if data["programs"][elem]["autorestart"] != "unexepected":
                                raise NameError("BAD_AR")
                    elif type(data["programs"][elem]["autorestart"]) != bool:
                        raise NameError("BAD_AR")
                #startretries
                if "startretries" in data["programs"][elem]:
                    if type(data["programs"][elem]["startretries"]) != int:
                        raise NameError("BAD_SR")
                #starttime
                if "starttime" in data["programs"][elem]:
                    if type(data["programs"][elem]["starttime"]) != int:
                        raise NameError("BAD_ST")
                #stopsignal
                list_signal = ["SIGTERM", "SIGINT", "SIGQUIT", "SIGHUP", "SIGKILL", "SIGUSR1", "SIGUSR2"]
                if "stopsignal" in data["programs"][elem]:
                    if type(data["programs"][elem]["stopsignal"]) != str:
                        raise NameError("BAD_SS")
                    if data["programs"][elem]["stopsignal"] not in list_signal:
                        raise NameError("BAD_SS")
                #stoptime
                if "stoptime" in data["programs"][elem]:
                    if type(data["programs"][elem]["stoptime"]) != int:
                        raise NameError("BAD_STT")
                #stdout
                if "stdout" in data["programs"][elem]:
                    if type(data["programs"][elem]["stdout"]) != str:
                        raise NameError("BAD_STDOUT")
                    if not os.path.exists(data["programs"][elem]["working_dir"]) or not\
                            os.path.isfile(data["programs"][elem]["working_dir"]) or os.path.isdir(data["programs"][elem]["working_dir"]):
                        raise NameError("BAD_STDOUT")
                #stderr
                if "stderr" in data["programs"][elem]:
                    if type(data["programs"][elem]["stderr"]) != str:
                        raise NameError("BAD_STDERR")
                    if not os.path.exists(data["programs"][elem]["working_dir"]) or not\
                            os.path.isfile(data["programs"][elem]["working_dir"]) or os.path.isdir(data["programs"][elem]["working_dir"]):
                        raise NameError("BAD_STDERR")
                #exitcodes
                if "exitcodes" in data["programs"][elem]:
                    if type(data["programs"][elem]["exitcodes"]) == list:
                        for elem in data["programs"][elem]["exitcodes"]:
                            if type(elem) != int:
                                raise NameError("BAD_EX")
                    elif type(data["programs"][elem]["exitcodes"]) != int:
                        raise NameError("BAD_EX")
        except NameError as e:
            if e.__str__() == "NO_CMD":
                print("Error: No cmd in config file")
            elif e.__str__() == "NO_PROG":
                print("Error: No programs in config file")
            elif e.__str__() == "BAD_NP":
                print("Error: numprocs invalid type, use int type")
            elif e.__str__() == "BAD_UM":
                print("Error: umask invalid type, use int type")
            elif e.__str__() == "BAD_WD":
                print("Error: workdir is invalid, use str type or file exist")
            elif e.__str__() == "BAD_AS":
                print("Error: autostart is invalid, use bool type")
            elif e.__str__() == "BAD_AR":
                print("Error: autorestart is invalid, use bool type or unexpected")
            elif e.__str__() == "BAD_SR":
                print("Error: startretries is invalid, use int type")
            elif e.__str__() == "BAD_ST":
                print("Error: starttime is invalid, use int type")
            elif e.__str__() == "BAD_SS":
                print("Error: stropsignal is invalid, use str type")
            elif e.__str__() == "BAD_STT":
                print("Error: stoptime is invalid, use int type")
            elif e.__str__() == "BAD_STDOUT":
                print("Error: stdout is invalid, use str type or file exist")
            elif e.__str__() == "BAD_STDERR":
                print("Error: stderr is invalid, use str type or file exist")
            elif e.__str__() == "BAD_EX":
                print("Error: exitcodes is invalid, use int type")
            else:
                print(e)
            sys.exit(-1)
        except Exception as e:
            print("Error: {}".format(e))
            sys.exit(0)

    def _clean_config(self, data):
        config = {}
        config["cmd"] = data["cmd"]
        if "numprocs" in data.keys():
            config["numprocs"] = data["numprocs"]
        else:
            config["numprocs"] = 1

        if "umask" in data.keys():
            config["umask"] = data["umask"]
        else:
            config["umask"] = 18 #022

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
            config["autorestart"] = "unexpected"

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
    
    def _refresh_conf_prog(self, name, configs):
        for prog in self.programs:
            if prog.name_prog == name:
                prog.refresh_conf(configs)
                return
        return
        
    def _reload_prog(self, name, configs):
        for prog in self.programs:
            if prog.name_prog == name:
                prog.reload(configs)
                return
        return

    def _reload_conf(self, signum, stack):
        new_configs = self._get_configs()
        for prog in self.programs:
            if prog.name_prog not in new_configs["programs"]:
                del prog
        for prog in self.configs["programs"]:
            if self.configs["programs"][prog]["numprocs"] !=  new_configs["programs"][prog]["numprocs"]:
                self._reload_prog(elem, new_configs["programs"][prog])
            elif self.configs["programs"][prog]["umask"] !=  new_configs["programs"][prog]["umask"]:
                self._reload_prog(elem, new_configs["programs"][prog])
            elif self.configs["programs"][prog]["working_dir"] !=  new_configs["programs"][prog]["working_dir"]:
                self._reload_prog(elem, new_configs["programs"][prog])
            elif self.configs["programs"][prog]["stdout"] !=  new_configs["programs"][prog]["stdout"]:
                self._reload_prog(elem, new_configs["programs"][prog])
            elif self.configs["programs"][prog]["stderr"] !=  new_configs["programs"][prog]["stderr"]:
                self._reload_prog(elem, new_configs["programs"][prog])
            elif self.configs["programs"][prog]["var_env"] !=  new_configs["programs"][prog]["var_env"]:
                self._reload_prog(elem, new_configs["programs"][prog])
            else:
                self._refresh_conf_prog(prog, new_configs["programs"][prog])
        self.configs = new_configs
        return

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
