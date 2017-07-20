from collections import namedtuple
from yyagl.gameobject import GameObject
from .logic import DriverLogic


DriverProps = namedtuple('DriverProps', 'name f_engine f_tires f_suspensions')


class DriverFacade(object):

    @property
    def dprops(self):
        return self.logic.dprops

class Driver(GameObject, DriverFacade):

    def __init__(self, driver_props):
        init_lst = [[('logic', DriverLogic, [self, driver_props])]]
        GameObject.__init__(self, init_lst)
