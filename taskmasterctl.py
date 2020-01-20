import socket
import sys

error_name_missing = "Error: {0} requires a process name\n\
{0} <name>\t\t{0} a process\n\
{0} <gname>:*  \t{0} all process in a group\n\
{0} <name> <name>\t{0} multiple processes or groups\n\
{0} all\t\t{0} all processes"

class Taskmasterclt():
    def __init__(self):
#        self.error_name_missing = "Error: {0} requires a process name\n\
#        {0} <name>\t\t{0} a process\n\
#        {0} <gname>:*  \t{0} all process in a group\n\
#        {0} <name> <name>\t{0} multiple processes or groups\n\
#        {0} all\t\t{0} all processes"
        self.dic_command = {
        "status" : self.status,
        "start" : self.start,
        "stop" : self.stop,
        "restart" : self.restart,
        "update" : self.null,
        "reload" : self.null, # restart the supervisord
        "pid" : self.null, # get the pid of supervisord
        "quit" : self.null,
        "shutdown" : self.null,
        "help" : self.print_help
        }
        self.host = 'localhost'
        self.port = 5678
        self.stream_serv = None
        self.create_connection()
        self.status(None, None)

    def create_connection(self):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((self.host, self.port))
        except Exception as e:
            print("Error: {}".format(e))
            sys.exit(0)
        self.stream_serv = sock
        return

    def send_and_recv_cmd(self, cmd, arg):
        msg = "{} {}".format(cmd, arg)
        msg = msg.encode()
        self.stream_serv.send(msg)
        msg = self.stream_serv.recv(1024)
        if msg == b'':
            print("taskamasterd not running")
            self.stream_serv.close()
            return
        print(msg.decode())
    
    def status(self, cmd, args):
        print("status fct")

    def start(self, cmd, args):
        if len(args) < 1:
            print(error_name_missing.format(cmd))
            return
        for elem in args:
            if elem == "all":
                self.send_and_recv_cmd(cmd, "all")
                return
        for elem in args:
            self.send_and_recv_cmd(cmd, elem)
    
    def stop(self, md, args):
        if len(args) < 1:
            print(error_name_missing.format(cmd))
            return
        for elem in args:
            if elem == "all":
                self.send_and_recv_cmd(cmd, "all")
                return
        for elem in args:
            self.send_and_recv_cmd(cmd, elem)
    
    def restart(self, cmd, args):
        if len(args) < 1:
            print(error_name_missing.format(cmd))
            return
        for elem in args:
            if elem == "all":
                self.send_and_recv_cmd(cmd, "all")
                return
        for elem in args:
            self.send_and_recv_cmd(cmd, elem)

    def null(self, cmd, args):
        print("{} not implemented yet".format(cmd))

    def print_help(cmd, args):
        print("help fct")

    def handle_cmd(self, cmd):
        args = cmd.split()
        if len(args) == 0:
            return 
        if args[0] not in self.dic_command:
            print("*** Unknown syntax: {}".format(args[0]))
            return 
        else:
            self.dic_command[args[0]](args.pop(0), args)


ctl = Taskmasterclt()

while True:
    cmd = input("taskmaster> ")
    ctl.handle_cmd(cmd)
