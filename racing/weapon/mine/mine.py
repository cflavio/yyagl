from yyagl.gameobject import GameObject
from .gfx import MineGfx
from .phys import MinePhys
from .audio import MineAudio
from .logic import MineLogic
from .event import MineEvent


class MineFacade(object):

    def attach_obs(self, meth):
        return self.logic.attach(meth)

    def detach_obs(self, meth):
        return self.logic.detach(meth)

    def fire(self):
        return self.logic.fire()


class Mine(GameObject, MineFacade):
    gfx_cls = MineGfx
    phys_cls = MinePhys
    audio_cls = MineAudio
    logic_cls = MineLogic
    event_cls = MineEvent

    def __init__(self, car, path, particle_path):
        init_lst = [
            [('gfx', self.gfx_cls, [self, car.gfx.nodepath, path])],
            [('phys', self.phys_cls, [self, car])],
            [('audio', self.audio_cls, [self])],
            [('logic', self.logic_cls, [self])],
            [('event', self.event_cls, [self, particle_path])]]
        GameObject.__init__(self, init_lst)
