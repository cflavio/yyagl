from yyagl.gameobject import GameObject
from yyagl.facade import Facade
from .gfx import WeaponGfx
from .audio import WeaponAudio


class WeaponFacade(Facade):

    def __init__(self):
        self._fwd_mth('attach_obs', lambda obj: obj.logic.attach)
        self._fwd_mth('detach_obs', lambda obj: obj.logic.detach)
        self._fwd_mth('fire', lambda obj: obj.logic.fire)
        self._fwd_mth('ai_fire', lambda obj: obj.ai.update)
        self._fwd_mth('reparent', lambda obj: obj.gfx.reparent)


class Weapon(GameObject, WeaponFacade):

    gfx_cls = WeaponGfx
    audio_cls = WeaponAudio
    deg = 0

    def __init__(self, car, path, cars, part_path):
        init_lst = [
            [('gfx', self.gfx_cls, [self, car.gfx.nodepath, path])],
            [('audio', self.audio_cls, [self])],
            [('logic', self.logic_cls, [self, car, cars])],
            [('ai', self.ai_cls, [self, car])]]
        GameObject.__init__(self, init_lst)
        WeaponFacade.__init__(self)

    def destroy(self):
        GameObject.destroy(self)
        WeaponFacade.destroy(self)


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
        # refactor: call Weapon.__init__
