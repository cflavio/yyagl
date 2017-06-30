from yyagl.gameobject import GameObject
from .gfx import RotateAllGfx
from .audio import RotateAllAudio
from .logic import RotateAllLogic


class RotateAllFacade(object):

    def attach_obs(self, meth):
        return self.logic.attach(meth)

    def detach_obs(self, meth):
        return self.logic.detach(meth)

    def fire(self):
        return self.logic.fire()


class RotateAll(GameObject, RotateAllFacade):
    gfx_cls = RotateAllGfx
    audio_cls = RotateAllAudio
    logic_cls = RotateAllLogic

    def __init__(self, car, path, cars):
        init_lst = [
            [('gfx', self.gfx_cls, [self, car.gfx.nodepath, path])],
            [('audio', self.audio_cls, [self])],
            [('logic', self.logic_cls, [self, car, cars])]]
        GameObject.__init__(self, init_lst)
