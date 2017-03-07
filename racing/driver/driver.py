from abc import ABCMeta
from yyagl.gameobject import GameObjectMdt
from .logic import DriverLogic


class Driver(GameObjectMdt):
    __metaclass__ = ABCMeta
    logic_cls = DriverLogic

    def __init__(self, name, engine, tires, suspensions):
        init_lst = [
            [('logic', self.logic_cls, [self, name, engine, tires,
                                        suspensions])]]
        GameObjectMdt.__init__(self, init_lst)
