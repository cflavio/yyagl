from random import uniform
from yyagl.gameobject import Ai


class RocketAi(Ai):

    def __init__(self, mdt):
        Ai.__init__(self, mdt)
        self.collect_time = globalClock.get_frame_time()
        self.fire_time = uniform(3, 15)

    def update(self):
        return not self.mdt.logic.has_fired and globalClock.get_frame_time() - self.collect_time > self.fire_time
