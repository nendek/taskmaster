from datetime import datetime
import time
import os
import threading
import sys
import signal

class Process:
    def __init__(self, name, logger):
        self.logger = logger
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
    
    def __str__(self):
        return "Process\n\tpid: {}\n\tstatus: {}\n\tstart_date: {}\n"\
        "\tend_date: {}\n\treturn_code: {}".format(self.pid, self.status, self.start_date, self.end_date, self.return_code)

    def start(self, data):
        if self.pid == 0:
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
                self.logger.info("process {} started".format(self.name_proc))
                self._create_listener()
                self.logger.info("process {} is now in STARTING state".format(self.name_proc))
                self.status = "STARTING"
                self.update_status()
                return
        return

    def quit(self):
        self.kill()
    
    def _create_listener(self):
        thread = threading.Thread(target=self._check_process_state, daemon=True)
        thread.start()
        return 

    def _check_process_state(self):
        try:
            status = os.waitpid(self.pid, 0)
            self.end_time = time.time()
            self.end_date = datetime.now()
            self.return_code = os.WEXITSTATUS(status[1])
            self.pid = 0
        except Exception as e:
            self.logger.error(e)
        finally:
            return
        return

    def update_status(self):
        now = time.time()
        if self.pid != 0: # process en cours
            if self.status == "RUNNING":
                pass
            if self.status == "STARTING":
                if now > self.start_time + self.starting_time:
                    self.status = "RUNNING"
                    self.logger.info("process {} is now in RUNNING state".format(self.name_proc))
                    self.nb_start = 0
            if self.status == "STOPPING":
                if now > self.stop_time + self.stopping_time:
                    self.kill()
        else: # process fini
            if self.status == "STARTING":
                if self.end_time < self.start_time + self.starting_time:
                    self.status = "BACKOFF"
                    self.logger.info("process {} is now in BACKOFF state".format(self.name_proc))
                else:
                    self.status = "EXITED"
                    self.logger.info("process {} is now in EXITED state".format(self.name_proc))
            if self.status == "RUNNING":
                self.status = "EXITED"
                self.logger.info("process {} is now in EXITED state".format(self.name_proc))
            if self.status == "STOPPING":
                self.status = "STOPPED"
                self.logger.info("process {} is now in STOPPED state".format(self.name_proc))


    def _launch_process(self, data):
        if data["fdout"] > 0:
            os.dup2(data["fdout"], sys.stdout.fileno())
        if data["fderr"] > 0:
            os.dup2(data["fderr"], sys.stderr.fileno())
        if data["working_dir"] != '.':
            try:
                os.chdir(data["working_dir"])
            except OSError as e:
                self.logger.error("cant chdir: {}".format(e))
        try:
            if type(data["umask"]) == str:
                os.umask(int(data["umask"], 8))
            else:
                os.umask(data["umask"])
        except OSError as e:
            self.logger.error("cant umask: {}".format(e))
        os.execve(data["cmd"], data["args"], data["env"])
        sys.exit()
    
    def kill(self):
        self._send_signal(signal.SIGKILL)

    def stop(self, stopsignal):
        self._send_signal(stopsignal)

    def _send_signal(self, signal): # put nb_start to 0
        try:
            if self.pid != 0:
                os.kill(self.pid, signal)
                self.status = "STOPPING"
                self.logger.info("process {} is now in STOPPING state".format(self.name_proc))
        except Exception as e:
            self.logger.error(e)
            return -1
        else:
            return 0

    def restart(self, data):
        self.kill()
        self.start(data)
