from random import uniform
from yyagl.gameobject import Ai


class RotateAllAi(Ai):

    def __init__(self, mdt):
        Ai.__init__(self, mdt)
        self.collect_time = globalClock.get_frame_time()
        self.fire_time = uniform(3, 15)

    def update(self):
        return globalClock.get_frame_time() - self.collect_time > self.fire_time
