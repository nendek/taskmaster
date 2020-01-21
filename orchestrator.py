import yaml
import time
import signal
import os
import sys
from program import Program

class Orchestrator():
    def __init__(self, config_file_name, logger):
        self.logger = logger
        self.path = os.path.join(os.path.abspath(os.path.dirname(config_file_name)), config_file_name)
        self.configs = {}
        self.configs = self._get_configs()
        self.programs = []
        signal.signal(signal.SIGHUP, self.reload_conf)

    def start(self):
        progs = []
        for elem in self.configs["programs"]:
            progs.append(Program(self.configs["programs"][elem], elem, self.logger))
        self.programs = progs
        self.logger.info("taskmasterd well started")
        return
    
    def quit(self):
        for prog in self.programs:
            prog.quit()
            del prog
        self.logger.info("supervisord shutdown")

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
        string = ""
        self.update_processes()
        self.logger.info("status request received")
        for program in self.programs:
            for proc in program.process:
                if proc.pid != 0:
                    string += "{:30} {:10} pid {:10} uptime      {}\n".format(proc.name_proc, proc.status, proc.pid, time.strftime("%H:%M:%S", time.gmtime(time.time() - proc.start_time)))
                else:
                    if proc.end_time == 0:
                        string += "{:30} {:10}\n".format(proc.name_proc, proc.status)
                    else:
                        string += "{:30} {:25} {}\n".format(proc.name_proc, proc.status, time.strftime("%b %d %Y %H:%M:%S", time.gmtime(proc.end_time)))
        return string

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
                self.logger.warning("Error: YAML file format error {}".format(e))
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
                    if not os.path.exists(data["programs"][elem]["stdout"]) or not\
                            os.path.isfile(data["programs"][elem]["stdout"]) or os.path.isdir(data["programs"][elem]["stdout"]):
                        raise NameError("BAD_STDOUT")

                #stderr
                if "stderr" in data["programs"][elem]:
                    if type(data["programs"][elem]["stderr"]) != str:
                        raise NameError("BAD_STDERR")
                    if not os.path.exists(data["programs"][elem]["stderr"]) or not\
                            os.path.isfile(data["programs"][elem]["stderr"]) or os.path.isdir(data["programs"][elem]["stderr"]):
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
                self.logger.warning("Error: No cmd in config file")
                print("Error: No cmd in config file")
            elif e.__str__() == "NO_PROG":
                self.logger.warning("Error: No programs in config file")
                print("Error: No programs in config file")
            elif e.__str__() == "BAD_NP":
                self.logger.warning("Error: numprocs invalid type, use int type")
                print("Error: numprocs invalid type, use int type")
            elif e.__str__() == "BAD_UM":
                self.logger.warning("Error: umask invalid type, use int type")
                print("Error: umask invalid type, use int type")
            elif e.__str__() == "BAD_WD":
                self.logger.warning("Error: workdir is invalid, use str type or file exist")
                print("Error: workdir is invalid, use str type or file exist")
            elif e.__str__() == "BAD_AS":
                self.logger.warning("Error: autostart is invalid, use bool type")
                print("Error: autostart is invalid, use bool type")
            elif e.__str__() == "BAD_AR":
                self.logger.warning("Error: autorestart is invalid, use bool type or unexpected")
                print("Error: autorestart is invalid, use bool type or unexpected")
            elif e.__str__() == "BAD_SR":
                self.logger.warning("Error: startretries is invalid, use int type")
                print("Error: startretries is invalid, use int type")
            elif e.__str__() == "BAD_ST":
                self.logger.warning("Error: starttime is invalid, use int type")
                print("Error: starttime is invalid, use int type")
            elif e.__str__() == "BAD_SS":
                self.logger.warning("Error: stropsignal is invalid, use str type")
                print("Error: stropsignal is invalid, use str type")
            elif e.__str__() == "BAD_STT":
                self.logger.warning("Error: stoptime is invalid, use int type")
                print("Error: stoptime is invalid, use int type")
            elif e.__str__() == "BAD_STDOUT":
                self.logger.warning("Error: stdout is invalid, use str type or file exist")
                print("Error: stdout is invalid, use str type or file exist")
            elif e.__str__() == "BAD_STDERR":
                self.logger.warning("Error: stderr is invalid, use str type or file exist")
                print("Error: stderr is invalid, use str type or file exist")
            elif e.__str__() == "BAD_EX":
                self.logger.warning("Error: exitcodes is invalid, use int type")
                print("Error: exitcodes is invalid, use int type")
            else:
                print("Error: {}".format(e))
                print(e)
            sys.exit(-1)
        except Exception as e:
            print(e)
            self.logger.warning("Error: {}".format(e))
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
            config["working_dir"] = os.getcwd()

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

    def reload_conf(self, signum, stack):
        self.logger.info("loading config file")
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
        self.logger.info("config file well loaded")
        return

    def _same_configs(self, dic1, dic2):
        return True

    def start_all_proc(self):
        self.logger.info("start all request received")
        response = ""
        for program in self.programs:
            response += program.start_all()
        return response

    def start_proc(self, name):
        self.logger.info("start {} request received".format(name))
        response = ""
        for program in self.programs:
            if program.start(name):
                response = "{:30} started\n".format(name)
                return response
        response = "{:30} not exist\n".format(name)
        return response
    
    def kill_all_proc(self):
        self.logger.info("kill all request received")
        response = ""
        for program in self.programs:
            response += program.kill_all()
        return response

    def kill_proc(self, name):
        self.logger.info("kill {} request received".format(name))
        response = ""
        for program in self.programs:
            if program.kill(name):
                response = "{:30} killed\n".format(name)
                return response
        response = "{:30} not exist\n".format(name)
        return response
    
    def stop_all_proc(self):
        self.logger.info("stop all request received")
        response = ""
        for program in self.programs:
            response += program.stop_all()
        return response

    def stop_proc(self, name):
        self.logger.info("stop {} request received".format(name))
        response = ""
        for program in self.programs:
            if program.stop(name):
                response = "{:30} stopped\n".format(name)
                return response
        response = "{:30} not exist\n".format(name)
        return response
    
    def restart_all_proc(self):
        self.logger.info("restart all request received")
        response = ""
        for program in self.programs:
            response += program.restart_all()
        return response

    def restart_proc(self, name):
        self.logger.info("restart {} request received".format(name))
        response = ""
        for program in self.programs:
            if program.restart(name):
                response = "{:30} restarted\n".format(name)
                return response
        response = "{:30} not exist\n".format(name)
        return response
