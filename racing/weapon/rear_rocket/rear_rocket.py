from yyagl.gameobject import GameObject
from .gfx import RearRocketGfx
from .phys import RearRocketPhys
from .audio import RearRocketAudio
from .logic import RearRocketLogic


class RearRocketFacade(object):

    def attach_obs(self, meth):
        return self.logic.attach(meth)

    def detach_obs(self, meth):
        return self.logic.detach(meth)

    def fire(self):
        return self.logic.fire()


class RearRocket(GameObject, RearRocketFacade):
    gfx_cls = RearRocketGfx
    phys_cls = RearRocketPhys
    audio_cls = RearRocketAudio
    logic_cls = RearRocketLogic

    def __init__(self, car, path):
        init_lst = [
            [('gfx', self.gfx_cls, [self, car.gfx.nodepath, path])],
            [('phys', self.phys_cls, [self, car.gfx.nodepath])],
            [('audio', self.audio_cls, [self])],
            [('logic', self.logic_cls, [self])]]
        GameObject.__init__(self, init_lst)
