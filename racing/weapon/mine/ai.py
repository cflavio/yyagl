from random import uniform
from yyagl.gameobject import Ai


class MineAi(Ai):

    def __init__(self, mdt, car):
        Ai.__init__(self, mdt)
        self.collect_time = globalClock.get_frame_time()
        self.car = car
        self.fire_time = uniform(2, 5)

    def update(self):
        if self.mdt.logic.has_fired or globalClock.get_frame_time() - self.collect_time < self.fire_time:
            return
        return self.car.ai.is_on_road
