# this kills yorg when it is being launched by geany
from subprocess import Popen, PIPE
from os import system


def exec_cmd(cmd):
    ret = Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True).communicate()
    return '\n'.join(ret)


processes_str = exec_cmd('ps aux | grep "python main.py"')
processes = list(enumerate(processes_str.split('\n')))
sh_cmd = ' /bin/sh -c python main.py'
geany_row = [proc for proc in processes if proc[1].endswith(sh_cmd)][0][0]
geany_pid = list(processes)[geany_row + 1][1].split()[1]
system('kill -9 ' + geany_pid)
