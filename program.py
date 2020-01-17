from process import Process
import os
import signal

class Program:
    def __init__(self, config, name):
        self.name = name
        self.process = []
        self.data = {}
        self.env = os.environ.copy()
        self._load_config(config)
        for i in range(0, self.numprocs):
            self.process.append(Process())
            if self.autostart == True:
                self.process[i].start(self.data)

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
            self.autorestart = "unexepected"

        if "startretries" in config.keys():
            self.startretries = config["startretries"]
        else:
            self.startretries = 3

        if "starttime" in config.keys():
            self.starttime = config["starttime"]
        else:
            self.starttime = 1

        if "stopsignal" in config.keys():
            sig_conf = config["stopsignal"]
            if sig_conf == signal.SIGTERM.name:
                self.stopsignal = signal.SIGTERM
            elif sig_conf == signal.SIGINT.name:
                self.stopsignal = signal.SIGINT
            elif sig_conf == signal.SIGQUIT.name:
                self.stopsignal = signal.SIGQUIT
            elif sig_conf == signal.SIGHUP.name:
                self.stopsignal = signal.SIGHUP
            elif sig_conf == signal.SIGKILL.name:
                self.stopsignal = signal.SIGKILL
            elif sig_conf == signal.SIGUSR1.name:
                self.stopsignal = signal.SIGUSR1
            elif sig_conf == signal.SIGUSR2.name:
                self.stopsignal = signal.SIGUSR2
            else:
                #log pas le bon signal de stop
                self.stopsignal = signal.SIGTERM
        else:
            self.stopsignal = signal.SIGTERM

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
            self.var_env = config["env"].copy()
        else:
            self.var_env = {}

        self.bin, self.args = self.parse_cmd()
        self._update_data()
        

    def __str__(self):
        return "Program:\nname: {}\nprocessus: {}\ncmd: {}\nnumprocs: {}\numask: {}\nworking_dir: {}\n"\
        "autostart: {}\nautoretart: {}\nstartentries: {}\nstarttime: {}\nstopsignal: {}\n"\
        "stoptime: {}\nstdout: {}\nstderr: {}\nexitcodes: {}\nenv: {}".format(self.name, self.process, self.cmd, self.numprocs, self.umask, self.working_dir, self.autostart, self.autorestart,
                self.startretries, self.starttime, self.stopsignal, self.stoptime, self.stdout, self.stderr, self.exitcodes, self.env)

    def parse_cmd(self):
        tab = self.cmd.split()
        return tab.pop(0), tab
    
    def _set_env(self):
        for key, value in self.var_env.items():
            self.data["env"][key] = value
        return

    def _set_args(self):
        self.data["args"].insert(0, self.bin)
        return

    def _update_data(self):
        self.env = os.environ.copy()
        self.data["cmd"] = self.bin
        self.data["args"] = self.args
        self._set_args()
        self.data["env"] = self.env
        self._set_env()
        self.data["fdout"] = self.fdout
        self.data["fderr"] = self.fderr
        self.data["working_dir"] = self.working_dir
        self.data["umask"] = self.umask
        self.data["starttime"] = self.starttime
        self.data["stoptime"] = self.stoptime
        self.data["startretries"] = self.startretries
        return
    
    def kill_all(self):
        for process in self.process:
            process.kill()
        return
    
    def kill(self, pid):
        for process in self.process:
            if pid == process.pid:
                process.kill()
                return 1
        return 0

    def stop_all(self):
        for process in self.process:
            process.stop(self.stopsignal)
        return

    def stop(self, pid):
        for process in self.process:
            if pid == process.pid:
                process.stop(self.stopsignal)
                return 1
        return 0
