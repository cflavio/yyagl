from yyagl.gameobject import GameObject
from yyagl.facade import Facade
from .gfx import RocketGfx
from .phys import RocketPhys
from .audio import RocketAudio
from .logic import RocketLogic
from .event import RocketEvent
from .ai import RocketAi


class RocketFacade(Facade):

    def __init__(self):
        self._fwd_mth('attach_obs', self.logic.attach)
        self._fwd_mth('detach_obs', self.logic.detach)
        self._fwd_mth('fire', self.logic.fire)
        self._fwd_mth('ai_fire', self.ai.update)
        self._fwd_mth('reparent', self.gfx.reparent)


class Rocket(GameObject, RocketFacade):

    def __init__(self, car, path, cars, particle_path):
        init_lst = [
            [('gfx', RocketGfx, [self, car.gfx.nodepath, path])],
            [('phys', RocketPhys, [self, car, cars])],
            [('audio', RocketAudio, [self])],
            [('logic', RocketLogic, [self])],
            [('event', RocketEvent, [self, particle_path])],
            [('ai', RocketAi, [self, car])]]
        GameObject.__init__(self, init_lst)
        RocketFacade.__init__(self)
