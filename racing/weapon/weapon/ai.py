from random import uniform
from yyagl.gameobject import Ai


class WeaponAi(Ai):

    fire_times = (2, 5)

    def __init__(self, mdt, car):
        Ai.__init__(self, mdt)
        self.collect_time = globalClock.get_frame_time()
        self.car = car
        self.fire_time = uniform(*self.fire_times)

    @property
    def is_fired_or_before(self):
        is_before_fire = eng.curr_time - self.collect_time < self.fire_time
        return self.mdt.logic.has_fired or is_before_fire

    @property
    def obstacles(self):
        return list(self.car.ai.front_logic.get_obstacles())

    @property
    def rear_obstacles(self):
        return list(self.car.ai.rear_logic.get_obstacles())