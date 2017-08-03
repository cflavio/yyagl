from yyagl.gameobject import GameObject
from yyagl.facade import Facade
from .gfx import RearRocketGfx
from .phys import RearRocketPhys
from .audio import RearRocketAudio
from .logic import RearRocketLogic
from .event import RearRocketEvent
from .ai import RearRocketAi


class RearRocketFacade(Facade):

    def __init__(self):
        self._fwd_mth('attach_obs', self.logic.attach)
        self._fwd_mth('detach_obs', self.logic.detach)
        self._fwd_mth('fire', self.logic.fire)
        self._fwd_mth('ai_fire', self.ai.update)


class RearRocket(GameObject, RearRocketFacade):
    gfx_cls = RearRocketGfx
    phys_cls = RearRocketPhys
    audio_cls = RearRocketAudio
    logic_cls = RearRocketLogic
    event_cls = RearRocketEvent
    ai_cls = RearRocketAi

    def __init__(self, car, path, cars, particle_path):
        init_lst = [
            [('gfx', self.gfx_cls, [self, car.gfx.nodepath, path])],
            [('phys', self.phys_cls, [self, car, cars])],
            [('audio', self.audio_cls, [self])],
            [('logic', self.logic_cls, [self])],
            [('event', self.event_cls, [self, particle_path])],
            [('ai', self.ai_cls, [self, car])]]
        GameObject.__init__(self, init_lst)
        RearRocketFacade.__init__(self)
