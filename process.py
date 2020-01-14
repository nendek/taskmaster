from datetime import datetime

class Process:
    def __init__(self):
        self.pid = 0
        self.state = "stop"
        self.start_date = 0

    def __str__(self):
        return "Process\npid: {}\nstate: {}\nstart_date: {}\n".format(self.pid, self.state, self.start_date)

    def start(cmd, argv, env):
        '''
        faire un pipe
fork
enfant :
    close(pipe[0]) # enfant qui peut ecrire sur le pipe
    fd = open(file_name_stdout)
    dup2(fd, STDOUT)
    fd = open(file_name_stderr)
    dup2(fd, STDERR)
    #write start in pipe
    try:
        execve(cmd, arg, env)
    except:
        #write stop in pipe
        write(pipe, "ERROR", len(ERROR))
    #write exited in pipe
    write(pipre, return code, len(return_code)
    exit()
parent :
    for all_process:
        nb = read(pipe[0])
        if nb != 0:
            do some stuff`'''
        try:
            pid = os.fork()
        except:
            return -1
        self.start_date = datetime.now()
        if pid == 0:
            try:
                os.execve(cmd, argv, env)
            except:
                exit(-1)
        else:
            self.pid = pid
        
