from random import uniform
from yyagl.racing.weapon.weapon.ai import WeaponAi


class RotateAllAi(WeaponAi):

    fire_times = (3, 15)

    def update(self):
        is_after_fire = self.eng.curr_time - self.collect_time > self.fire_time
        return not self.mdt.logic.has_fired and is_after_fire
