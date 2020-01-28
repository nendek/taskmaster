from process import Process
import os
import signal

class Program():
    def __init__(self, config, name, fdnull, logger):
        self.logger = logger
        self.name_prog = name
        self.process = []
        self.fdnull = fdnull
        self.config = self._load_config(config)
        self._launch_process()

    def quit(self):
        for process in self.process:
            process.quit()
            del process
        if self.config["stdout"] != False:
            os.close(self.config["fdout"])
        if self.config["stderr"] != False:
            os.close(self.config["fderr"])

    def _launch_process(self):
        self.process = []
        for i in range(0, self.config["numprocs"]):
            if self.config["numprocs"] <= 1:
                self.process.append(Process(self.name_prog, self.config, self.logger))
            else:
                self.process.append(Process("{}:{}".format(self.name_prog, i), self.config, self.logger))
            if self.config["autostart"] == True:
                self.process[i].start()

    def _load_config(self, config):
        config["fdnull"] = self.fdnull
        try:
            if config["stdout"] == False:
                config["fdout"] = config["fdnull"]
            else:
                config["fdout"] = os.open(config["stdout"], os.O_WRONLY | os.O_CREAT | os.O_APPEND)
    
            if config["stderr"] == False:
                config["fderr"] = config["fdnull"]
            else:
                config["fderr"] = os.open(config["stderr"], os.O_WRONLY | os.O_CREAT | os.O_APPEND)
        except Exception as e:
            self.logger.error("error on handling std : {}".format(e))
            raise Exception # TODO : fix l'exception a raise
        for key, val in os.environ.items():
            config["env"][key] = val
        config["bin"], config["args"] = self.parse_cmd(config["cmd"])
        return config
        

    def __str__(self):
        return "Program:\nname: {}\nprocessus: {}\ncmd: {}\nnumprocs: {}\numask: {}\nworking_dir: {}\n"\
        "autostart: {}\nautoretart: {}\nstartentries: {}\nstarttime: {}\nstopsignal: {}\n"\
        "stoptime: {}\nstdout: {}\nstderr: {}\nexitcodes: {}\nenv: {}".format(self.name, self.process, self.cmd, self.numprocs, self.umask, self.working_dir, self.autostart, self.autorestart,
                self.startretries, self.starttime, self.stopsignal, self.stoptime, self.stdout, self.stderr, self.exitcodes, self.env)

    def parse_cmd(self, cmd):
        tab = cmd.split()
        return tab[0], tab
    
    """
#    def refresh_conf(self, config):
#        self._load_config(config)
#
#    def reload(self, config):
#        self._load_config(config)
#        self.kill_all()
#        del self.process
#        self._launch_process()
    def kill_all(self):
        response = ""
        for process in self.process:
            response += "{:30} killed\n".format(process.name_proc)
            process.kill()
        return response
    
    def kill(self, name):
        for process in self.process:
            if name == process.name_proc:
                process.kill()
                return 1
        return 0

    def stop_all(self):
        response = ""
        for process in self.process:
            response += "{:30} stopped\n".format(process.name_proc)
            process.stop(self.stopsignal)
        return response

    def stop(self, name):
        for process in self.process:
            if name == process.name_proc:
                process.stop(self.stopsignal)
                return 1
        return 0
    
    def start_all(self):
        response = ""
        for process in self.process:
            response += "{:30} started\n".format(process.name_proc)
            process.start(self.data)
        return response

    def start(self, name):
        for process in self.process:
            if name == process.name_proc:
                process.start(self.data)
                return 1
        return 0
    
    def restart_all(self):
        response = ""
        for process in self.process:
            response += "{:30} restarted\n".format(process.name_proc)
            process.restart(self.data)
        return response

    def restart(self, name):
        for process in self.process:
            if name == process.name_proc:
                process.restart(self.data)
                return 1
        return 0

"""
