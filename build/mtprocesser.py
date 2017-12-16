from datetime import datetime
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
            print datetime.now().strftime("%H:%M:%S"), cmd
            system(cmd)


class ProcesserNoThreaded:

    def __init__(self, cmd_lst):
        self.cmd_lst = cmd_lst

    def run(self):
        for cmd in self.cmd_lst:
            print datetime.now().strftime("%H:%M:%S"), cmd
            system(cmd)


class MultithreadedProcesser(object):

    def __init__(self, cores):
        try: self.cores = cpu_count()
        except NotImplementedError: self.cores = 1
        self.cores = cores if cores else self.cores / 4 + 1
        print 'mt-processer: using %s cores' % self.cores
        self.cmd_lst = []

    def add(self, cmd):
        self.cmd_lst += [cmd]

    def run(self):
        if self.cores != 1:
            threads = []
            lock = RLock()
            for i in range(self.cores):
                threads += [Processer(self.cmd_lst, lock)]
            for thread in threads:
                thread.start()
            for thread in threads:
                thread.join()
        else:
            ProcesserNoThreaded(self.cmd_lst).run()
