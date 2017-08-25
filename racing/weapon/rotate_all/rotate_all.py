from yyagl.gameobject import GameObject
from yyagl.facade import Facade
from .gfx import RotateAllGfx
from .audio import RotateAllAudio
from .logic import RotateAllLogic
from .ai import RotateAllAi


class RotateAllFacade(Facade):

    def __init__(self):
        self._fwd_mth('attach_obs', self.logic.attach)
        self._fwd_mth('detach_obs', self.logic.detach)
        self._fwd_mth('fire', self.logic.fire)
        self._fwd_mth('ai_fire', self.ai.update)
        self._fwd_mth('reparent', self.gfx.reparent)


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
        RotateAllFacade.__init__(self)
