from cProfile import Profile
from pstats import Stats
from StringIO import StringIO
from ..singleton import Singleton


class Profiler(object):

    __metaclass__ = Singleton

    def __init__(self, enabled):
        self.enabled = enabled
        if not enabled:
            return
        self.prof = Profile()
        self.stats = None

    def enable(self):
        if not self.enabled:
            return
        self.prof.enable()

    def disable(self):
        if not self.enabled:
            return
        self.prof.disable()

    def printstats(self):
        self.prof.disable()
        sio = StringIO()
        self.stats = Stats(self.prof, stream=sio).sort_stats('cumulative')
        if not self.enabled:
            return
        self.stats.print_stats()
        print sio.getvalue()
        # lines = sio.getvalue().split('\n')
        # out_lines = lines[:5]
        # lines = lines[5:]
        # lines = [line.split() for line in lines]
        # lines = [line for line in lines if line]
        # lines = reversed(sorted(lines, key=lambda line: line[4]))
        # lines = ['\t'.join(line) for line in lines]
        # print '\n'.join(out_lines + lines)
