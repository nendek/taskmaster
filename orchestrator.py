import yaml
import time
from program import Program

class Orchestrator():
    def __init__(self, config_file_name):
        self.programs = self.start(config_file_name)

    def start(self, filename):
        with open(filename) as f:
            try:
                progs = []
                data = yaml.safe_load(f)
                if not "programs" in data.keys():
                    raise NameError("NO_PROG")
                for elem in data["programs"]:
                    if not "cmd" in data["programs"][elem]:
                        raise NameError("NO_CMD")
                for elem in data["programs"]:
                    progs.append(Program(data["programs"][elem], elem))
            except yaml.YAMLError as e:
                print("YAML file format error:")
                print(e)
            except NameError as e:
                if e.__str__() == "NO_CMD":
                    print("No cmd in config file")
                elif e.__str__() == "NO_PROG":
                    print("No programs in config file")
                else:
                    raise e
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
                    process.start()
                if program.autorestart == True:
                    if process.status in ["STOPPED", "EXITED"]:
                        process.start()
                if program.autorestart == "unexpeced":
                    if process.status == "EXITED":
                        if process.return_code not in program.exitcodes:
                            process.start()
    def show_processes(self):
        self.update_processes()
        for program in self.programs:
            print("nom du programme: {}".format(program.name))
            for process in program.process:
                print(process)
            print("")
