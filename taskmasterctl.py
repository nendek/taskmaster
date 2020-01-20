import socket
import sys

host = 'localhost'
port = 5678

def create_connection():
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((host, port))
    except Exception as e:
        print("Error: {}".format(e))
        sys.exit(0)
    return sock

stream_serv = create_connection()

error_name_missing = "Error: {0} requires a process name\n\
{0} <name>\t\t{0} a process\n\
{0} <gname>:*  \t{0} all process in a group\n\
{0} <name> <name>\t{0} multiple processes or groups\n\
{0} all\t\t{0} all processes"

def null(cmd, args):
    print("{} not implemented yet".format(cmd))

def status(cmd, args):
    print("status fct")

def start(cmd, args):
    if len(args) < 1:
        print(error_name_missing.format(cmd))
        return
    for elem in args:
        if elem == "all":
            send_and_recv_cmd(cmd, "all")
            return
    for elem in args:
        send_and_recv_cmd(cmd, elem)

def stop(cmd, args):
    if len(args) < 1:
        print(error_name_missing.format(cmd))
        return
    for elem in args:
        if elem == "all":
            send_and_recv_cmd(cmd, "all")
            return
    for elem in args:
        send_and_recv_cmd(cmd, elem)

def restart(cmd, args):
    if len(args) < 1:
        print(error_name_missing.format(cmd))
        return
    for elem in args:
        if elem == "all":
            send_and_recv_cmd(cmd, "all")
            return
    for elem in args:
        send_and_recv_cmd(cmd, elem)

def print_help(cmd, args):
    print("help fct")

dic_command = {
"status" : status,
"start" : start,
"stop" : stop,
"restart" : restart,
"update" : null,
"reload" : null, # restart the supervisord
"pid" : null, # get the pid of supervisord
"quit" : null,
"shutdown" : null,
"help" : print_help
}

def handle_cmd(cmd):
    args = cmd.split()
    if len(args) == 0:
        return 
    if args[0] not in dic_command:
        print("*** Unknown syntax: {}".format(args[0]))
        return 
    else:
        dic_command[args[0]](args.pop(0), args)

def send_and_recv_cmd(cmd, arg):
    msg = "{} {}".format(cmd, arg)
    msg = msg.encode()
    stream_serv.send(msg)
    msg = stream_serv.recv(1024)
    if msg == b'':
        print("taskamasterd not running")
        socket.close()
        return
    print(msg.decode())


status(None, None)

while True:
    cmd = input("taskmaster> ")
    handle_cmd(cmd)
