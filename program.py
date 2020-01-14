class Program:
    def __init__(self, config, name):
        self.name = name
        self.process = []
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
        else:
            self.stdout = "false"

        if "stderr" in config.keys():
            self.stderr = config["stderr"]
        else:
            self.stderr = "false"

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
        
    def __str__(self):
        return "Program:\nname: {}\nprocessus: {}\ncmd: {}\nnumprocs: {}\numask: {}\nworking_dir: {}\n"\
        "autostart: {}\nautoretart: {}\nstartentries: {}\nstarttime: {}\nstopsignal: {}\n"\
        "stoptime: {}\nstdout: {}\nstderr: {}\nexitcodes: {}\nenv: {}".format(self.name, self.process, self.cmd, self.numprocs, self.umask, self.working_dir, self.autostart, self.autorestart,
                self.startretries, self.starttime, self.stopsignal, self.stoptime, self.stdout, self.stderr, self.exitcodes, self.env)

