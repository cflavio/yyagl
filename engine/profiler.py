from os.path import exists


if not exists('main.pyo'):  # we don't deploy cProfile
    from cProfile import Profile
    from pstats import Stats
    from StringIO import StringIO


class AbsProfiler(object):

    @staticmethod
    def build(percall):
        prof_cls = AbsProfiler
        if not exists('main.pyo'):
            prof_cls = PerCallProfiler if percall else Profiler
        return prof_cls(percall)

    def __init__(self, percall): pass

    def printstats(self): pass

    def toggle(self): pass


class Profiler(AbsProfiler):

    def __init__(self, percall):
        self.percall = percall
        self.is_profiling = False  # we can't infer from cProfile
        self.prof = Profile()
        self.stats = None

    def toggle(self):
        if not self.is_profiling: self.__enable()
        else:
            self.__disable()
            self.printstats()

    def __enable(self):
        self.prof.enable()
        self.is_profiling = True

    def __disable(self):
        self.prof.disable()
        self.is_profiling = False

    def printstats(self):
        self.prof.disable()
        sio = StringIO()
        self.stats = Stats(self.prof, stream=sio).sort_stats('cumulative')
        self.stats.print_stats()
        self._print_lines(sio)

    def _print_lines(self, sio):
        print sio.getvalue()


class PerCallProfiler(Profiler):

    def _print_lines(self, sio):
        lines = sio.getvalue().split('\n')
        header_lines = lines[:5]
        content_lines = [line.split() for line in lines[5:] if line]
        sorted_lines = reversed(sorted(content_lines, key=lambda line: line[4]))
        # line[4] is the percall value
        joined_lines = ['\t'.join(line) for line in sorted_lines]
        print '\n'.join(header_lines + joined_lines)
