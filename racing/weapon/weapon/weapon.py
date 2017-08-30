from yyagl.gameobject import GameObject
from yyagl.facade import Facade
from .gfx import WeaponGfx
from .phys import WeaponPhys
from .audio import WeaponAudio
from .logic import WeaponLogic
from .event import WeaponEvent
from .ai import WeaponAi


class WeaponFacade(Facade):

    def __init__(self):
        self._fwd_mth('attach_obs', self.logic.attach)
        self._fwd_mth('detach_obs', self.logic.detach)
        self._fwd_mth('fire', self.logic.fire)
        self._fwd_mth('ai_fire', self.ai.update)
        self._fwd_mth('reparent', self.gfx.reparent)


class Weapon(GameObject, WeaponFacade):

    gfx_cls = WeaponGfx
    audio_cls = WeaponAudio

    def __init__(self, car, path, cars, part_path):
        init_lst = [
            [('gfx', self.gfx_cls, [self, car.gfx.nodepath, path])],
            [('audio', self.audio_cls, [self])],
            [('logic', self.logic_cls, [self, car, cars])],
            [('ai', self.ai_cls, [self, car])]]
        GameObject.__init__(self, init_lst)
        WeaponFacade.__init__(self)


class PhysWeapon(Weapon):

    def __init__(self, car, path, cars, part_path):
        init_lst = [
            [('gfx', self.gfx_cls, [self, car.gfx.nodepath, path])],
            [('phys', self.phys_cls, [self, car, cars])],
            [('audio', self.audio_cls, [self])],
            [('logic', self.logic_cls, [self, car, cars])],
            [('event', self.event_cls, [self, part_path])],
            [('ai', self.ai_cls, [self, car])]]
        GameObject.__init__(self, init_lst)
        WeaponFacade.__init__(self)
