from yyagl.gameobject import GameObject
from yyagl.facade import Facade
from .logic import DriverLogic


class Driver(GameObject):

    def __init__(self, img_idx, name, speed, adherence, stability):
        GameObject.__init__(self)
        self.img_idx = img_idx
        self.name = name
        self.speed = speed
        self.adherence = adherence
        self.stability = stability

    def __repr__(self):
        return 'driver(%s %s %s %s %s)' % (
            self.img_idx, self.name, self.speed, self.adherence, self.stability)
