import yaml
import signal
import os

class ParsingError(Exception):
    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)

class Config_parser():
    def __init__(self, config_file_name):
#        self.logger = logger
        self.path = os.path.join(os.path.abspath(os.path.dirname(config_file_name)), config_file_name)
        self.configs = {"programs": {}}
        self.default_config = {
            "numprocs": 1,
            "umask": 18,
            "working_dir": os.getcwd(),
            "autostart": True,
            "autorestart": "unexpected",
            "startretries": 3,
            "starttime": 1,
            "stopsignal": signal.SIGTERM,
            "stoptime": 10,
            "stdout": False,
            "stderr": False,
            "exitcodes": [0],
            "env": {}
        }


    def parse_config(self):
        self.configs = {"programs": {}}
        try:
            with open(self.path) as f:
                data = yaml.safe_load(f)
                self._parse_yaml(data)
        except Exception as e:
            raise ParsingError(e.__str__())
            
    def _parse_yaml(self, data):
        for program in data.values():
            for name, params in program.items():
                self.configs["programs"][name] = self.default_config.copy()
                for key, val in params.items():
                    self._check_type(key, val, name)
                    if key == "stopsignal":
                        val = self._transform_stopsignal(key, val, name)
                    self.configs["programs"][name][key] = val

    def _check_type(self, key, val, name):
        if key in ["numprocs", "umask", "working_dir", "autostart", "startretries", "starttime", "stoptime", "env"]:
            if type(self.default_config[key]) != type(val):
                raise ParsingError("Error in type of {} for program {}".format(key, name))
        if key == "autorestart":
            if val != False and val != True and val != "unexpected":
                raise ParsingError("Error in type of {} for program {}".format(key, name))
        if key == "stdout" or key == "stderr":
            if val != False and os.path.isdir(val):
                raise ParsingError("Error in type of {} for program {}".format(key, name))
        if key == "exitcodes":
            if type(val) != list:
                raise ParsingError("Error in type of {} for program {}".format(key, name))
            for elem in val:
                if type(elem) != int:
                    raise ParsingError("Error in type of {} for program {}".format(key, name))

    def _transform_stopsignal(self, key, val, name):
        if val == signal.SIGTERM.name:
            return signal.SIGTERM
        if val == signal.SIGINT.name:
            return signal.SIGINT
        if val == signal.SIGQUIT.name:
            return signal.SIGQUIT
        if val == signal.SIGHUP.name:
            return signal.SIGHUP
        if val == signal.SIGKILL.name:
            return signal.SIGKILL
        if val == signal.SIGUSR1.name:
            return signal.SIGUSR1
        if val == signal.SIGUSR2.name:
            return signal.SIGUSR2
        raise ParsingError("Error in type of {} for program {}".format(key, name))
