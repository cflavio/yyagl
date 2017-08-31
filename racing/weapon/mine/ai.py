from random import uniform
from yyagl.racing.weapon.weapon.ai import WeaponAi


class MineAi(WeaponAi):

    def update(self):
        if self.is_fired_or_before: return
        return self.car.ai.is_on_road
