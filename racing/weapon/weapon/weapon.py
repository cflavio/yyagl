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

    def __init__(self, car, path, cars, part_path, wpn_id, players):
        GameObject.__init__(self)
        self.gfx = self.gfx_cls(self, car.gfx.nodepath, path)
        self.audio = self.audio_cls(self)
        self.logic = self.logic_cls(self, car, cars, wpn_id)
        self.ai = self.ai_cls(self, car)
        WeaponFacade.__init__(self)

    def destroy(self):
        self.gfx.destroy()
        self.audio.destroy()
        self.logic.destroy()
        self.ai.destroy()
        GameObject.destroy(self)
        WeaponFacade.destroy(self)


class PhysWeapon(Weapon):

    def __init__(self, car, path, cars, part_path, wpn_id, players):
        GameObject.__init__(self)
        self.gfx = self.gfx_cls(self, car.gfx.nodepath, path)
        self.phys = self.phys_cls(self, car, cars, players)
        self.audio = self.audio_cls(self)
        self.logic = self.logic_cls(self, car, cars, wpn_id)
        self.event = self.event_cls(self, part_path)
        self.ai = self.ai_cls(self, car)
        WeaponFacade.__init__(self)
        # refactor: call Weapon.__init__

    def destroy(self):
        self.phys.destroy()
        self.event.destroy()
        Weapon.destroy(self)
