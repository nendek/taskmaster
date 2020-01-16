from datetime import datetime
import time
import os
import sys

class Process:
    def __init__(self):
        self.pid = 0
        self.status = "NOT STARTED"
        self.start_date = None
        self.start_time = 0
        self.end_date = None
        self.return_code = None

    def __str__(self):
        return "Process\n\tpid: {}\n\tstatus: {}\n\tstart_date: {}\n"\
        "\tend_date: {}\n\treturn_code: {}".format(self.pid, self.status, self.start_date, self.end_date, self.return_code)

    def start(self, data):
        self.start_date = datetime.now()
        self.start_time = time.time()
        pid = os.fork()
        if pid == 0: # child
            self._launch_process(data)
        else:
            self.pid = pid
            self.update_child_status()
            return 

    def _launch_process(self, data):
        if data["fdout"] > 0:
            os.dup2(data["fdout"], sys.stdout.fileno())
        if data["fderr"] > 0:
            os.dup2(data["fderr"], sys.stderr.fileno())
        if data["working_dir"] != '.':
            try:
                os.chdir(data["working_dir"])
            except OSError as e:
                print("cant chdir: {}".format(e))
        try:
            os.umask(int(data["umask"], 8))
        except OSError as e:
            print("cant umask: {}".format(e))
        os.execve(data["cmd"], data["args"], data["env"])
        sys.exit()

    def update_child_status(self):
        self.end_date = None
        self.status = self._get_child_status()
        return 0

    def _get_child_status(self):
        status = os.waitpid(self.pid, os.WNOHANG)
        if status[0] == 0:
            return "RUNNING"
        else:
            self.return_code = os.WEXITSTATUS(status[1])
            self.end_date = datetime.now()
            self.pid = None
            return "FINISHED"

    def send_signal(self, signal):
        try:
            os.kill(self.pid, signal)
            self.status = "KILLED"
        except Exception as e:
            print(e)
            return -1
        else:
            return 0

    def restart(self, signal):
        self.stop(signal)
        self.start()
