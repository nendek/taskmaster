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
            send_cmd(cmd, "all")
            return
    for elem in args:
        send_cmd(cmd, elem)



def stop(cmd, args):
    if len(args) < 1:
        print(error_name_missing.format(cmd))
        return
    for elem in args:
        if elem == "all":
            send_cmd(cmd, "all")
            return
    for elem in args:
        send_cmd(cmd, elem)

def restart(cmd, args):
    if len(args) < 1:
        print(error_name_missing.format(cmd))
        return
    for elem in args:
        if elem == "all":
            send_cmd(cmd, "all")
            return
    for elem in args:
        send_cmd(cmd, elem)

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

def parse_cmd(cmd):
    args = cmd.split()
    if len(args) == 0:
        return 
    if args[0] not in dic_command:
        print("*** Unknown syntax: {}".format(args[0]))
        return 
    else:
        dic_command[args[0]](args.pop(0), args)


status(None, None)

def send_cmd(cmd, arg):
    print("{} {}".format(cmd, arg))

while True:
    cmd = input("taskmaster> ")
    parse_cmd(cmd)
