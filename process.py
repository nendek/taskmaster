from datetime import datetime
import time
import os
import threading
import sys
import signal

class Process:
    def __init__(self, name, config, logger):
        self.logger = logger
        self.name_proc = name
        self.config = config
        self.pid = 0
        self.status = "STOPPED"
        self.nb_start = 0

        self.started_time = 0 # time when process has been stated
        self.stopped_time = 0 # time when process received signal stop
        self.ended_time = 0 # time when process has terminate

        self.return_code = None # return code of the process when exited
    
    def __str__(self):
        return "Process\n\tpid: {}\n\tstatus: {}\n\t"\
        "\t\treturn_code: {}".format(self.pid, self.status, self.return_code)

    def _set_status(self, status):
        self.status = status
        self.logger.info("process {} is now in {} state".format(self.name_proc, status))

    def _send_signal(self, signal): # put nb_start to 0
        try:
            if self.pid != 0:
                self.nb_start = 0
                os.kill(self.pid, signal)
                self.update_status()
        except Exception as e:
            self.logger.debug(self.pid)
            self.logger.error(e)

    def _create_listener(self):
        thread = threading.Thread(target=self._check_process_state, daemon=True)
        thread.start()
        return 

    def _check_process_state(self):
        try:
            status = os.waitpid(self.pid, 0)
            self.ended_time = time.time()
            self.return_code = os.WEXITSTATUS(status[1])
            self.pid = 0
        except Exception as e:
            self.logger.error(e)
        return

    def _launch_process(self):
        try:
            os.dup2(self.config["fdout"], sys.stdout.fileno())
            os.dup2(self.config["fderr"], sys.stderr.fileno())
            os.chdir(self.config["working_dir"])
            os.umask(self.config["umask"])
            os.execve(self.config["bin"], self.config["args"], self.config["env"])
        except Exception as e:
            self.logger.error("Error on launchig process {}: {}".format(self.name_proc, e))
        sys.exit()
    
    def start(self):
        if self.pid == 0:
            self.nb_start += 1
            if (self.nb_start > self.config["startretries"]):
                self._set_status("FATAL")
                return 
            self.started_time = time.time()
            self.ended_time = 0
            try:
                pid = os.fork()
            except Exception as e:
                self.logger.warning("Error fork: {}".format(e))
                return
            if pid == 0: # child
                self._launch_process()
            else:
                self.pid = pid
                self.logger.info("process {} started".format(self.name_proc))
                self._create_listener()
                self._set_status("STARTING")
                self.update_status()
                return
        return

    def stop(self, stopsignal):
        self._send_signal(stopsignal)
        self._set_status("STOPPING")
        self.stopped_time = time.time()

    def quit(self):
        self._send_signal(signal.SIGKILL)
    
    def update_status(self):
        now = time.time()
        if self.pid != 0: # process en cours
            if self.status == "RUNNING":
                pass
            if self.status == "STARTING":
                if now > self.started_time + self.config["starttime"]:
                    self._set_status("RUNNING")
                    self.nb_start = 0
            if self.status == "STOPPING":
                if now > self.stopped_time + self.config["stoptime"]:
                    self.quit()
        else: # process fini
            if self.status == "STARTING":
                if self.ended_time < self.started_time + self.config["starttime"]:
                    self._set_status("BACKOFF")
                else:
                    self._set_status("EXITED")
            if self.status == "RUNNING":
                self._set_status("EXITED")
            if self.status == "STOPPING":
                self._set_status("STOPPED")
