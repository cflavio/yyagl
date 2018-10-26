from direct.interval.MetaInterval import Sequence
from direct.interval.FunctionInterval import Wait
from direct.interval.LerpInterval import LerpPosInterval
from direct.interval.FunctionInterval import Func
from yyagl.facade import Facade


class P3dSeq(Facade):

    def __init__(self, *ivals):
        self.seq = Sequence(*[ival.ival for ival in ivals])
        self._fwd_mth('start', lambda obj: obj.seq.start)

    def append(self, ival): return self.seq.append(ival.ival)


class P3dWait(object):

    def __init__(self, time): self.ival = Wait(time)


class P3dPosIval(object):

    def __init__(self, np, time=1.0, pos=(0, 0, 0), blend_type='ease'):
        blend2p3d = {'ease': 'easeInOut'}
        self.ival = LerpPosInterval(np, time, pos=pos,
                                    blendType=blend2p3d[blend_type])


class P3dFunc(object):

    def __init__(self, fun, *args): self.ival = Func(fun, *args)
