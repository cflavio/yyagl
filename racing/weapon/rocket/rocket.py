from yyagl.gameobject import GameObject
from .gfx import RocketGfx
from .phys import RocketPhys
from .audio import RocketAudio
from .logic import RocketLogic
from .event import RocketEvent


class RocketFacade(object):

    def attach_obs(self, meth):
        return self.logic.attach(meth)

    def detach_obs(self, meth):
        return self.logic.detach(meth)

    def fire(self):
        return self.logic.fire()


class Rocket(GameObject, RocketFacade):
    gfx_cls = RocketGfx
    phys_cls = RocketPhys
    audio_cls = RocketAudio
    logic_cls = RocketLogic
    event_cls = RocketEvent

    def __init__(self, car, path, cars):
        init_lst = [
            [('gfx', self.gfx_cls, [self, car.gfx.nodepath, path])],
            [('phys', self.phys_cls, [self, car, cars])],
            [('audio', self.audio_cls, [self])],
            [('logic', self.logic_cls, [self])],
            [('event', self.event_cls, [self])]]
        GameObject.__init__(self, init_lst)
