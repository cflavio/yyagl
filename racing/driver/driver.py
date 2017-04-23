from yyagl.gameobject import GameObject
from .logic import DriverLogic


class DriverProps(object):

    def __init__(self, name, engine, tires, suspensions):
        self.name = name
        self.engine = engine
        self.tires = tires
        self.suspensions = suspensions


class Driver(GameObject):

    def __init__(self, driver_props):
        init_lst = [[('logic', DriverLogic, [self, driver_props])]]
        GameObject.__init__(self, init_lst)
