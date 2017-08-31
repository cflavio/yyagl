from random import uniform
from yyagl.racing.weapon.weapon.ai import WeaponAi


class RearRocketAi(WeaponAi):

    def update(self):
        if self.is_fired_or_before: return
        closest_center, closest_left, closest_right = self.rear_obstacles
        return closest_center.dist < 40 and closest_center.name == 'Vehicle'
