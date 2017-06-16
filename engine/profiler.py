import cProfile, pstats, StringIO
from ..singleton import Singleton


class Profiler(object):

    __metaclass__ = Singleton

    def __init__(self, enabled):
        self.enabled = enabled
        if not enabled:
            return
        self.pr = cProfile.Profile()

    def enable(self):
        if not self.enabled:
            return
        self.pr.enable()

    def disable(self):
        if not self.enabled:
            return
        self.pr.disable()

    def printstats(self):
        self.pr.disable()
        s = StringIO.StringIO()
        self.ps = pstats.Stats(self.pr, stream=s).sort_stats('cumulative')
        if not self.enabled:
            return
        self.ps.print_stats()
        print s.getvalue()
        #lines = s.getvalue().split('\n')
        #out_lines = lines[:5]
        #lines = lines[5:]
        #lines = [line.split() for line in lines]
        #lines = [line for line in lines if line]
        #lines = reversed(sorted(lines, key=lambda line: line[4]))
        #lines = ['\t'.join(line) for line in lines]
        #print '\n'.join(out_lines + lines)
