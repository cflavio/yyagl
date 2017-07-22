from yyagl.gameobject import GameObject
from yyagl.facade import Facade
from .gfx import MineGfx
from .phys import MinePhys
from .audio import MineAudio
from .logic import MineLogic
from .event import MineEvent
from .ai import MineAi


class MineFacade(Facade):

    def __init__(self):
        self._fwd_mth('attach_obs', self.logic.attach)
        self._fwd_mth('detach_obs', self.logic.detach)
        self._fwd_mth('fire', self.logic.fire)
        self._fwd_mth('ai_fire', self.ai.update)


class Mine(GameObject, MineFacade):
    gfx_cls = MineGfx
    phys_cls = MinePhys
    audio_cls = MineAudio
    logic_cls = MineLogic
    event_cls = MineEvent
    ai_cls = MineAi

    def __init__(self, car, path, particle_path):
        init_lst = [
            [('gfx', self.gfx_cls, [self, car.gfx.nodepath, path])],
            [('phys', self.phys_cls, [self, car])],
            [('audio', self.audio_cls, [self])],
            [('logic', self.logic_cls, [self])],
            [('event', self.event_cls, [self, particle_path])],
            [('ai', self.ai_cls, [self, car])]]
        GameObject.__init__(self, init_lst)
        MineFacade.__init__(self)