from yyagl.gameobject import GameObject
from yyagl.facade import Facade
from .gfx import TurboGfx
from .audio import TurboAudio
from .logic import TurboLogic
from .ai import TurboAi


class TurboFacade(Facade):

    def __init__(self):
        self._fwd_mth('attach_obs', self.logic.attach)
        self._fwd_mth('detach_obs', self.logic.detach)
        self._fwd_mth('fire', self.logic.fire)
        self._fwd_mth('ai_fire', self.ai.update)


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
            [('ai', self.ai_cls, [self, car])]]
        GameObject.__init__(self, init_lst)
        TurboFacade.__init__(self)
