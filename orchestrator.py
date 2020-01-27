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
        self.fdnull = os.open("/dev/null", os.O_WRONLY)

    def start_orchestrator(self):
        progs = []
        for elem in self.configs["programs"]:
            progs.append(Program(self.configs["programs"][elem], elem, self.fdnull, self.logger))
        self.programs = progs
        self.logger.info("taskmasterd well started")
        return
    
    def quit_orchestrator(self):
        for prog in self.programs:
            prog.quit()
            del prog
        os.close(self.fdnull)
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
                    process.start()
                if program.config["autorestart"] == True:
                    if process.status == "EXITED":
                        process.start()
                if program.config["autorestart"] == "unexpected":
                    if process.status == "EXITED":
                        if process.return_code not in program.config["exitcodes"]:
                            process.start()

    def status(self):
        string = ""
        self.update_processes()
        for program in self.programs:
            for proc in program.process:
                if proc.pid != 0:
                    string += "{:30} {:10} pid {:10} uptime      {}\n".format(proc.name_proc, proc.status, proc.pid, time.strftime("%H:%M:%S", time.gmtime(time.time() - proc.started_time)))
                else:
                    if proc.ended_time == 0:
                        string += "{:30} {:10}\n".format(proc.name_proc, proc.status)
                    else:
                        string += "{:30} {:25} {}\n".format(proc.name_proc, proc.status, time.strftime("%b %d %Y %H:%M:%S", time.gmtime(proc.ended_time)))
        return string

    def update(self, new_configs):
        # 1 : delete les programmes qui ont disparus
        lst_to_del = []
        for prog in self.programs:
            if prog.name_prog not in new_configs["programs"].keys():
                prog.quit()
                lst_to_del.append(prog)
        for elem in lst_to_del:
            del self.programs[self.programs.index(elem)]

        # 2 : delete ceux qui restent avec une config diff
        lst_to_del = []
        for prog in self.programs:
            if self.same_config(prog.config, new_configs["programs"][prog.name_prog]) == False:
                prog.quit()
                lst_to_del.append(prog)
        for elem in lst_to_del:
            del self.programs[self.programs.index(elem)]

        # 3 : ajouter les nouveaux programmes
        for prog_name in new_configs["programs"]:
            if prog_name not in [elem.name_prog for elem in self.programs]:
                self.programs.append(Program(new_configs["programs"][prog_name], prog_name, self.fdnull, self.logger))
        self.configs = new_configs

    def same_config(self, dic_old, dic_new):
        for key, val in dic_new.items():
            if dic_old[key] != val:
                return False
        return True
        
    """
        return protocole for nexts functions :
            return 1 = started
            return 2 = already started
            return 0 = not found 
    """

    def start(self, name_proc):
        for program in self.programs:
            for proc in program.process:
                if proc.name_proc == name_proc:
                    if proc.status not in ["RUNNING", "STARTING"]:
                        proc.start()
                        return 1
                    else:
                        return 2
        return 0
    
    def stop(self, name_proc):
        for program in self.programs:
            for proc in program.process:
                if proc.name_proc == name_proc:
                    if proc.status in ["RUNNING", "STARTING"]:
                        proc.stop(program.config["stopsignal"])
                        while (proc.status != "STOPPED"):
                            pass
                        return 1
                    else:
                        return 2
        return 0

    def kill(self, name_proc):
        for program in self.programs:
            for proc in program.process:
                if proc.name_proc == name_proc:
                    if proc.status in ["RUNNING", "STARTING", "STOPPING"]:
                        proc.quit()
                        while (proc.status != "STOPPED"):
                            pass
                        return 1
                    else:
                        return 2
        return 0
