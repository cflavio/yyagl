# this kills yorg's server
from subprocess import Popen, PIPE
from os import system


def exec_cmd(cmd):
    ret = Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True).communicate()
    return '\n'.join(ret)


grep = "grep -E 'python.*server.*yorg.*main.py|python.*yorg.*server.*main.py'"
proc_line = exec_cmd('ps aux | ' + grep).split('\n')[0]
srv_pid = proc_line.split()[1]
system('kill -9 ' + srv_pid)
