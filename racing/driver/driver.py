from yyagl.gameobject import GameObjectMdt
from .logic import DriverLogic


class DriverProps(object):

    def __init__(self, name, engine, tires, suspensions):
        self.name = name
        self.engine = engine
        self.tires = tires
        self.suspensions = suspensions


class Driver(GameObjectMdt):

    def __init__(self, driver_props):
        init_lst = [[('logic', DriverLogic, [self, driver_props])]]
        GameObjectMdt.__init__(self, init_lst)
