from yyagl.gameobject import GameObject
from .gfx import RotateAllGfx
from .audio import RotateAllAudio
from .logic import RotateAllLogic
from .ai import RotateAllAi


class RotateAllFacade(object):

    def attach_obs(self, meth):
        return self.logic.attach(meth)

    def detach_obs(self, meth):
        return self.logic.detach(meth)

    def fire(self):
        return self.logic.fire()

    def ai_fire(self):
        return self.ai.update()


class RotateAll(GameObject, RotateAllFacade):
    gfx_cls = RotateAllGfx
    audio_cls = RotateAllAudio
    logic_cls = RotateAllLogic
    ai_cls = RotateAllAi

    def __init__(self, car, path, cars):
        init_lst = [
            [('gfx', self.gfx_cls, [self, car.gfx.nodepath, path])],
            [('audio', self.audio_cls, [self])],
            [('logic', self.logic_cls, [self, car, cars])],
            [('ai', self.ai_cls, [self])]]
        GameObject.__init__(self, init_lst)
