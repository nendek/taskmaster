from process import Process
import os
import signal

class Program:
    def __init__(self, config, name):
        self.name_prog = name
        self.process = []
        self.data = {}
        self.env = os.environ.copy()
        self._load_config(config)
        self._launch_process()

    def quit(self):
        for process in self.process:
            process.quit()
            del process

    def _launch_process(self):
        self.process = []
        for i in range(0, self.numprocs):
            if self.numprocs <= 1:
                self.process.append(Process(self.name_prog))
            else:
                self.process.append(Process("{}:{}".format(self.name_prog, i)))
            if self.autostart == True:
                self.process[i].start(self.data)

    def _load_config(self, config):
        self.cmd = config["cmd"]
        self.numprocs = config["numprocs"]
        self.umask = config["umask"]
        self.working_dir = config["working_dir"]
        self.autostart = config["autostart"]
        self.autorestart = config["autorestart"]
        self.startretries = config["startretries"]
        self.starttime = config["starttime"]
        self.stopsignal = config["stopsignal"]
        self.stoptime = config["stoptime"]

        if config["stdout"] != False:
            self.stdout = config["stdout"]
            self.fdout = os.open(self.stdout, os.O_WRONLY | os.O_CREAT | os.O_APPEND)
            if self.fdout < 0:
                self.fdout = -1
        else:
            self.stdout = False
            self.fdout = -1

        if config["stderr"] != False:
            self.stderr = config["stderr"]
            self.fderr = os.open(self.stderr, os.O_WRONLY | os.O_CREAT | os.O_APPEND)
            if self.fderr < 0:
                self.fderr = -1
        else:
            self.stderr = False
            self.fderr = -1
        self.exitcodes = config["exitcodes"]
        self.var_env = config["var_env"].copy()

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

    def refresh_conf(self, config):
        self._load_config(config)

    def reload(self, config):
        self._load_config(config)
        del self.process
        self._launch_process()
