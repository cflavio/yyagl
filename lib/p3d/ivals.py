from direct.interval.MetaInterval import Sequence
from direct.interval.FunctionInterval import Func, Wait
from direct.interval.LerpInterval import LerpPosInterval


class P3dSeq:

    def __init__(self, *ivals):
        self.seq = Sequence(*[ival._ival for ival in ivals])
        #TODO: don't access a protected member

    def start(self): return self.seq.start()

    def __add__(self, ival):
        self.seq.append(ival._ival)  #TODO: don't access a protected member
        return self.seq


class P3dWait:

    def __init__(self, time): self._ival = Wait(time)


class P3dPosIval:

    def __init__(self, node, time=1.0, pos=(0, 0, 0), blend_type='ease'):
        btype = {'ease': 'easeInOut'}[blend_type]
        self._ival = LerpPosInterval(node, time, pos=pos, blendType=btype)


class P3dFunc:

    def __init__(self, fun, *args): self._ival = Func(fun, *args)
