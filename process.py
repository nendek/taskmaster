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
        self.nb_start = 0
        self.max_start = 0

        self.start_time = 0
        self.starting_time = 0 # time to wait before STARTING to RUNNING state

        self.stop_time = 0
        self.stopping_time = 0 # time to wait before STOPPING to STOPPED state

        self.end_time = 0
        self.return_code = None
    
    def __str__(self):
        return "Process\n\tpid: {}\n\tstatus: {}\n\t"\
        "\t\treturn_code: {}".format(self.pid, self.status, self.return_code)

    def start(self, data):
        if self.pid == 0:
            self.nb_start += 1
            self.max_start = data["startretries"]
            if (self.nb_start > self.max_start):
                self.status = "FATAL"
                return 
            self.start_time = time.time()
            self.end_time = 0
            self.starting_time = data["starttime"]
            self.stopping_time = data["stoptime"]
            try:
                pid = os.fork()
            except Exception as e:
                self.logger.warning("Error fork: {}".format(e))
                return
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
        try:
            fd_null = os.open("/dev/null", os.O_WRONLY)
            if data["fdout"] > 0:
                os.dup2(data["fdout"], sys.stdout.fileno())
            else:
                os.dup2(fd_null, sys.stdout.fileno())
            if data["fderr"] > 0:
                os.dup2(data["fderr"], sys.stderr.fileno())
            else:
                os.dup2(fd_null, sys.stderr.fileno())
            os.close(fd_null)
            if data["working_dir"] != '.':
                os.chdir(data["working_dir"])
            os.umask(data["umask"])
            os.execve(data["cmd"], data["args"], data["env"])
        except Exception as e:
            self.logger.error("Error on launchig process: {}".format(e))
        sys.exit()
    
    def kill(self):
        self._send_signal(signal.SIGKILL)

    def stop(self, stopsignal):
        self._send_signal(stopsignal)
        self.stop_time = time.time()

    def _send_signal(self, signal): # put nb_start to 0
        try:
            if self.pid != 0:
                os.kill(self.pid, signal)
                self.status = "STOPPING"
                self.nb_start = 0
                self.logger.info("process {} is now in STOPPING state".format(self.name_proc))
        except Exception as e:
            self.logger.debug(self.pid)
            self.logger.error(e)
            return -1
        else:
            return 0

    def restart(self, data):
        self.kill()
        self.start(data)
