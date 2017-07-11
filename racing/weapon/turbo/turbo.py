from yyagl.gameobject import GameObject
from .gfx import TurboGfx
from .audio import TurboAudio
from .logic import TurboLogic
from .ai import TurboAi


class TurboFacade(object):

    def attach_obs(self, meth):
        return self.logic.attach(meth)

    def detach_obs(self, meth):
        return self.logic.detach(meth)

    def fire(self):
        return self.logic.fire()

    def ai_fire(self):
        return self.ai.update()


class Turbo(GameObject, TurboFacade):
    gfx_cls = TurboGfx
    audio_cls = TurboAudio
    logic_cls = TurboLogic
    ai_cls = TurboAi

    def __init__(self, car, path):
        init_lst = [
            [('gfx', self.gfx_cls, [self, car.gfx.nodepath, path])],
            [('audio', self.audio_cls, [self])],
            [('logic', self.logic_cls, [self, car])],
            [('ai', self.ai_cls, [self])]]
        GameObject.__init__(self, init_lst)
