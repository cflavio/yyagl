from multiprocessing import cpu_count
from subprocess import Popen, PIPE
from threading import Thread, RLock
from os import system


class Processer(Thread):

    def __init__(self, cmd_lst, lock):
        Thread.__init__(self)
        self.cmd_lst = cmd_lst
        self.lock = lock

    def run(self):
        while True:
            with self.lock:
                if not self.cmd_lst:
                    return
                cmd = self.cmd_lst.pop(0)
            print cmd
            system(cmd)


class MultithreadedProcesser(object):

    def __init__(self):
        try: self.cores = cpu_count()
        except NotImplementedError: self.cores = 1
        self.cores = self.cores / 2 + 1
        self.cmd_lst = []

    def add(self, cmd):
        self.cmd_lst += [cmd]

    def run(self):
        threads = []
        lock = RLock()
        for i in range(self.cores):
            threads += [Processer(self.cmd_lst, lock)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
