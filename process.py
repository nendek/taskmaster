from datetime import datetime
import time
import os
import threading
import sys
import signal

class Process:
    def __init__(self, name):
        self.name_proc = name
        self.pid = 0
        self.status = "STOPPED"
        self.start_date = None
        self.nb_start = 0
        self.max_start = 0

        self.start_time = 0
        self.starting_time = 0 # time to wait before STARTING to RUNNING state

        self.stop_time = 0
        self.stopping_time = 0 # time to wait before STOPPING to STOPPED state

        self.end_date = None
        self.end_time = None
        self.return_code = None

    def __del__(self):
        self.kill()
        print("process {} killed".format(self.name_proc))
    
    def __str__(self):
        return "Process\n\tpid: {}\n\tstatus: {}\n\tstart_date: {}\n"\
        "\tend_date: {}\n\treturn_code: {}".format(self.pid, self.status, self.start_date, self.end_date, self.return_code)

    def start(self, data):
        self.nb_start += 1
        self.max_start = data["startretries"]
        if (self.nb_start > self.max_start):
            self.status = "FATAL"
            return 
        self.start_date = datetime.now()
        self.start_time = time.time()
        self.end_time = None
        self.starting_time = data["starttime"]
        self.stopping_time = data["stoptime"]
        pid = os.fork()
        if pid == 0: # child
            self._launch_process(data)
        else:
            self.pid = pid
            self._create_listener()
            self.status = "STARTING"
            self.update_status()
            return 

    def _create_listener(self):
        thread = threading.Thread(target=self._check_process_state, daemon=True)
        thread.start()
        return 

    def _check_process_state(self):
        status = os.waitpid(self.pid, 0)
        self.end_time = time.time()
        self.end_date = datetime.now()
        self.return_code = os.WEXITSTATUS(status[1])
        self.pid = 0
        return

    def update_status(self):
        now = time.time()
        if self.pid != 0: # process en cours
            if self.status == "RUNNING":
                pass
            if self.status == "STARTING":
                if now > self.start_time + self.starting_time:
                    self.status = "RUNNING"
                    self.nb_start = 0
            if self.status == "STOPPING":
                if now > self.stop_time + self.stopping_time:
                    self.kill()
        else: # process fini
            if self.status == "STARTING":
                if self.end_time < self.start_time + self.starting_time:
                    self.status = "BACKOFF"
                else:
                    self.status = "EXITED"
            if self.status == "RUNNING":
                self.status = "EXITED"
            if self.status == "STOPPING":
                self.status = "STOPPED"


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
    
    def kill(self):
        self._send_signal(signal.SIGKILL)

    def stop(self, stopsignal):
        self._send_signal(stopsignal)

    def _send_signal(self, signal): # put nb_start to 0
        try:
            os.kill(self.pid, signal)
            self.status = "STOPPED"
        except Exception as e:
            print(e)
            return -1
        else:
            return 0

    def restart(self, data):
        self.kill()
        self.start(data)
