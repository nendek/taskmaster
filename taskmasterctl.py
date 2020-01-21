import readline
import socket
import sys

error_name_missing = "Error: {0} requires a process name\n\
{0} <name>\t\t{0} a process\n\
{0} <gname>:*  \t{0} all process in a group\n\
{0} <name> <name>\t{0} multiple processes or groups\n\
{0} all\t\t{0} all processes"

class bcolors:
    CMD = '\033[92m'
    FIRST = '\033[93m'
    ERR = '\033[91m'
    GB = '\033[35m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

class Taskmasterclt():
    def __init__(self):
        self.dic_command = {
        "status" : self.one_arg,
        "start" : self.multiple_arg,
        "stop" : self.multiple_arg,
        "restart" : self.multiple_arg,
        "update" : self.one_arg,
        "reload" : self.null, # restart the supervisord
        "pid" : self.one_arg, # get the pid of supervisord
        "quit" : self.quit,
        "shutdown" : self.one_arg,
        "help" : self.print_help
        }
        self.host = 'localhost'
        self.port = 5678
        self.stream_serv = None
        self.create_connection()
        self.one_arg("status", "")

    def create_connection(self):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((self.host, self.port))
        except Exception as e:
            print(f"{bcolors.ERR}", end='')
            print("Error: {}".format(e))
            print(f"{bcolors.ENDC}", end='')
            sys.exit(0)
        self.stream_serv = sock
        return

    def send_and_recv_cmd(self, cmd, arg):
        msg = "{} {}".format(cmd, arg)
        msg = msg.encode()
        self.stream_serv.send(msg)
        msg = self.stream_serv.recv(1024)
        if msg == b'':
            print(f"{bcolors.ERR}taskmasterd not running{bcolors.ENDC}")
            self.stream_serv.close()
            return
        print(f"{bcolors.ENDC}", end='')
        print(msg.decode())
    
    def one_arg(self, cmd, args):
        self.send_and_recv_cmd(cmd, "")

    def multiple_arg(self, cmd, args):
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
    
    def quit(self, cmd, args):
        print(f"{bcolors.GB}{bcolors.BOLD}Goodbye Bro...{bcolors.ENDC}")
        sys.exit(0)
    
    def print_help(cmd, args):
        print("help fct")

    def handle_cmd(self, cmd):
        args = cmd.split()
        if len(args) == 0:
            return 
        if args[0] not in self.dic_command:
            print(f"{bcolors.ERR}", end='')
            print("*** Unknown syntax: {}".format(args[0]))
            return 
        else:
            self.dic_command[args[0]](args.pop(0), args)

print(f"{bcolors.GB}{bcolors.BOLD}Hello Bro !{bcolors.ENDC}")
cmds = ["status", "start", "stop", "restart", "update", "reload", "pid", "quit", "shutdown", "help"]

def completion(text, state):
    matches = [s for s in cmds if s and s.startswith(text)]
    try:
        return matches[state] + ' '
    except IndexError:
        return None
        
ctl = Taskmasterclt()
readline.set_completer(completion)
readline.parse_and_bind('tab: complete')

while True:
    cmd = input(f"{bcolors.FIRST}{bcolors.BOLD}taskmaster> {bcolors.ENDC}{bcolors.CMD}")
    ctl.handle_cmd(cmd)
