from process import Process
import os

class Program:
    def __init__(self, config, name):
        self.name = name
        self.process = []
        self._load_config(config)
        for i in range(0, self.numprocs):
            self.process.append(Process())
            if self.autostart == True:
                self.process[i].start(self.bin, self.args, self.env, self.fdout, self.fderr)

    def _load_config(self, config):
        self.cmd = config["cmd"]
        if "numprocs" in config.keys():
            self.numprocs = config["numprocs"]
        else:
            self.numprocs = 1

        if "umask" in config.keys():
            self.umask = config["umask"]
        else:
            self.umask = "022"

        if "working_dir" in config.keys():
            self.working_dir = config["working_dir"]
        else:
            self.working_dir = "."

        if "autostart" in config.keys():
            self.autostart = config["autostart"]
        else:
            self.autostart = True

        if "autorestart" in config.keys():
            self.autorestart = config["autorestart"]
        else:
            self.autorestart = -1 #unexepected

        if "startretries" in config.keys():
            self.startretries = config["startretries"]
        else:
            self.startretries = 3

        if "starttime" in config.keys():
            self.starttime = config["starttime"]
        else:
            self.starttime = 1

        if "stopsignal" in config.keys():
            self.stopsignal = config["stopsignal"]
        else:
            self.stopsignal = "TERM"

        if "stoptime" in config.keys():
            self.stoptime = config["stoptime"]
        else:
            self.stoptime = 10

        if "stdout" in config.keys():
            self.stdout = config["stdout"]
            self.fdout = os.open(self.stdout, os.O_WRONLY | os.O_CREAT | os.O_APPEND)
            if self.fdout < 0:
                self.fdout = -1
        else:
            self.stdout = False
            self.fdout = -1

        if "stderr" in config.keys():
            self.stderr = config["stderr"]
            self.fderr = os.open(self.stderr, os.O_WRONLY | os.O_CREAT | os.O_APPEND)
            if self.fderr < 0:
                self.fderr = -1
        else:
            self.stderr = False
            self.fderr = -1

        if "exitcodes" in config.keys():
            self.exitcodes = []
            if type(config["exitcodes"]) == int:
                self.exitcodes.append(config["exitcodes"])
            else:
                for elem in config["exitcodes"]:
                    self.exitcodes.append(elem)
        else:
            self.exitcodes = [0]

        if "env" in config.keys():
            self.env = config["env"].copy()
        else:
            self.env = {}

        self.bin, self.args = self.parse_cmd()
        

    def __str__(self):
        return "Program:\nname: {}\nprocessus: {}\ncmd: {}\nnumprocs: {}\numask: {}\nworking_dir: {}\n"\
        "autostart: {}\nautoretart: {}\nstartentries: {}\nstarttime: {}\nstopsignal: {}\n"\
        "stoptime: {}\nstdout: {}\nstderr: {}\nexitcodes: {}\nenv: {}".format(self.name, self.process, self.cmd, self.numprocs, self.umask, self.working_dir, self.autostart, self.autorestart,
                self.startretries, self.starttime, self.stopsignal, self.stoptime, self.stdout, self.stderr, self.exitcodes, self.env)

    def parse_cmd(self):
        tab = self.cmd.split()
        return tab.pop(0), tab
        
