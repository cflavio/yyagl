from random import uniform
from yyagl.gameobject import AiColleague


class WeaponAi(AiColleague):

    fire_times = (2, 5)

    def __init__(self, mediator, car):
        AiColleague.__init__(self, mediator)
        self.collect_time = self.eng.curr_time
        self.car = car
        self.fire_time = uniform(*self.fire_times)

    @property
    def is_fired_or_before(self):
        before_fire = self.eng.curr_time - self.collect_time < self.fire_time
        return self.mediator.logic.has_fired or before_fire

    @property
    def obstacles(self):
        return list(self.car.ai.front_logic.get_obstacles())

    @property
    def rear_obstacles(self):
        return list(self.car.ai.rear_logic.get_obstacles())
