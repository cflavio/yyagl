from yyagl.gameobject import GameObjectMdt
from .logic import DriverLogic


class Driver(GameObjectMdt):

    def __init__(self, name, engine, tires, suspensions):
        init_lst = [
            [('logic', DriverLogic, [self, name, engine, tires, suspensions])]]
        GameObjectMdt.__init__(self, init_lst)
