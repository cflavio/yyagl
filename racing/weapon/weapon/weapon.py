from yyagl.gameobject import GameObject
from yyagl.facade import Facade
from .gfx import WeaponGfx
from .audio import WeaponAudio


class WeaponFacade(Facade):

    def __init__(self):
        prop_lst = [('id', lambda obj: obj.logic.wpn_id)]
        mth_lst = [
            ('attach_obs', lambda obj: obj.logic.attach),
            ('detach_obs', lambda obj: obj.logic.detach),
            ('fire', lambda obj: obj.logic.fire),
            ('update_props', lambda obj: obj.logic.update_props),
            ('update_fired_props', lambda obj: obj.logic.update_fired_props),
            ('ai_fire', lambda obj: obj.ai.update),
            ('reparent', lambda obj: obj.gfx.reparent)]
        Facade.__init__(self, prop_lst, mth_lst)


class Weapon(GameObject, WeaponFacade):

    gfx_cls = WeaponGfx
    audio_cls = WeaponAudio
    deg = 0

    def __init__(self, car, path, cars, part_path, wpn_id):
        init_lst = [
            [('gfx', self.gfx_cls, [self, car.gfx.nodepath, path])],
            [('audio', self.audio_cls, [self])],
            [('logic', self.logic_cls, [self, car, cars, wpn_id])],
            [('ai', self.ai_cls, [self, car])]]
        GameObject.__init__(self, init_lst)
        WeaponFacade.__init__(self)

    def destroy(self):
        GameObject.destroy(self)
        WeaponFacade.destroy(self)


class PhysWeapon(Weapon):

    def __init__(self, car, path, cars, part_path, wpn_id):
        init_lst = [
            [('gfx', self.gfx_cls, [self, car.gfx.nodepath, path])],
            [('phys', self.phys_cls, [self, car, cars])],
            [('audio', self.audio_cls, [self])],
            [('logic', self.logic_cls, [self, car, cars, wpn_id])],
            [('event', self.event_cls, [self, part_path])],
            [('ai', self.ai_cls, [self, car])]]
        GameObject.__init__(self, init_lst)
        WeaponFacade.__init__(self)
        # refactor: call Weapon.__init__
