from random import uniform
from yyagl.gameobject import Ai


class RotateAllAi(Ai):

    def __init__(self, mdt, car):
        Ai.__init__(self, mdt)
        self.collect_time = globalClock.get_frame_time()
        self.fire_time = uniform(3, 15)

    def update(self):
        curr_t = globalClock.get_frame_time()
        is_after_fire = curr_t - self.collect_time > self.fire_time
        return not self.mdt.logic.has_fired and is_after_fire
