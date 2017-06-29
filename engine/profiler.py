# refactor it. since cProfile is not picked by packp3d i should manage that.
from os.path import exists


if not exists('main.pyo'):
    from cProfile import Profile
    from pstats import Stats
    from StringIO import StringIO
    from ..singleton import Singleton


    class Profiler(object):

        __metaclass__ = Singleton

        def __init__(self, enabled, percall):
            self.enabled = enabled
            self.percall = percall
            self.is_profiling = False
            if not enabled:
                return
            self.prof = Profile()
            self.stats = None

        def enable(self):
            if not self.enabled:
                return
            self.prof.enable()
            self.is_profiling = True

        def disable(self):
            if not self.enabled:
                return
            self.prof.disable()
            self.is_profiling = False

        def toggle(self):
            if not self.enabled:
                return
            if not self.is_profiling:
                self.enable()
            else:
                self.disable()
                self.printstats()

        def printstats(self):
            self.prof.disable()
            sio = StringIO()
            self.stats = Stats(self.prof, stream=sio).sort_stats('cumulative')
            if not self.enabled:
                return
            self.stats.print_stats()
            if not self.percall:
                print sio.getvalue()
            else:
                lines = sio.getvalue().split('\n')
                out_lines = lines[:5]
                lines = lines[5:]
                lines = [line.split() for line in lines]
                lines = [line for line in lines if line]
                lines = reversed(sorted(lines, key=lambda line: line[4]))
                lines = ['\t'.join(line) for line in lines]
                print '\n'.join(out_lines + lines)


else:
    from ..singleton import Singleton


    class Profiler(object):

        __metaclass__ = Singleton

        def __init__(self, enabled):
            pass

        def enable(self):
            pass

        def disable(self):
            pass

        def printstats(self):
            pass
