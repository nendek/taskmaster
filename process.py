from datetime import datetime
import os

class Process:
    def __init__(self):
        self.pid = 0
        self.state = "stop"
        self.start_date = 0
        self.fd_w = 0
        self.fd_r = 0

    def __str__(self):
        return "Process\npid: {}\nstate: {}\nstart_date: {}\n"\
                "fd_w: {}\nfd_r: {}".format(self.pid, self.state, self.start_date, self.fd_w, self.fd_r)

    def start(self):
        try:
            self.fd_r, self.fd_w = os.pipe()
            pid = os.fork()
        except:
            return -1

        self.start_date = datetime.now()
        if pid == 0:
            os.close(self.fd_r)
            w = os.fdopen(self.fd_w, 'w')
            w.write("start")
            w.close()
            while True:
                i = 0
                i += 1
            #ret = os.execve(cmd, argv, env)
            #if ret == -1: #voir try execpt
            #    w = os.fdopen(self.fd_w, 'w')
            #    w.write('error')
            #    w.close()
            #    sys.exit(-1)
            #w = os.fdopen(self.fd_w, 'w')
            #w.write('stop')
            #w.close()
            sys.exit(0)
        else:
            self.pid = pid
            self.update_child_status()
        return 0

    def update_child_status(self):
        if self.fd_w <= 0 and self.fd_r <= 0:
            self.status = "error"
            return -1
        os.close(self.fd_w)
        r = os.fdopen(self.fd_r)
        status = r.read()
        r.close()
        self.state = status
        return 0

    def stop(self, signal):
        try:
            os.kill(self.pid, signal)
            self.state = "kill"
        except Exception as e:
            print(e)
            return -1
        else:
            return 0

    def restart(self, signal):
        self.stop(signal)
        self.start()
