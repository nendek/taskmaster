#import yaml
import time
import signal
import os
import sys
from program import Program

class Orchestrator():
    def __init__(self, configs, logger):
        self.logger = logger
        self.programs = []
        self.configs = configs
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
                self._reload_prog(prog, new_configs["programs"][prog])
            elif self.configs["programs"][prog]["umask"] !=  new_configs["programs"][prog]["umask"]:
                self._reload_prog(prog, new_configs["programs"][prog])
            elif self.configs["programs"][prog]["working_dir"] !=  new_configs["programs"][prog]["working_dir"]:
                self._reload_prog(prog, new_configs["programs"][prog])
            elif self.configs["programs"][prog]["stdout"] !=  new_configs["programs"][prog]["stdout"]:
                self._reload_prog(prog, new_configs["programs"][prog])
            elif self.configs["programs"][prog]["stderr"] !=  new_configs["programs"][prog]["stderr"]:
                self._reload_prog(prog, new_configs["programs"][prog])
            elif self.configs["programs"][prog]["var_env"] !=  new_configs["programs"][prog]["var_env"]:
                self._reload_prog(prog, new_configs["programs"][prog])
            elif self.configs["programs"][prog]["autostart"] !=  new_configs["programs"][prog]["autostart"]:
                self._reload_prog(prog, new_configs["programs"][prog])
            elif self.configs["programs"][prog]["autorestart"] !=  new_configs["programs"][prog]["autorestart"]:
                self._reload_prog(prog, new_configs["programs"][prog])
            elif self.configs["programs"][prog]["startretries"] !=  new_configs["programs"][prog]["startretries"]:
                self._reload_prog(prog, new_configs["programs"][prog])
            elif self.configs["programs"][prog]["exitcodes"] !=  new_configs["programs"][prog]["exitcodes"]:
                self._reload_prog(prog, new_configs["programs"][prog])
            elif self.configs["programs"][prog]["starttime"] !=  new_configs["programs"][prog]["starttime"]:
                self._reload_prog(prog, new_configs["programs"][prog])

            else:
                self._refresh_conf_prog(prog, new_configs["programs"][prog])
        self.configs = new_configs
        self.logger.info("config file well loaded")
        return

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
