from collections import namedtuple
from yyagl.gameobject import GameObject
from yyagl.facade import Facade
from .logic import DriverLogic


DriverProps = namedtuple('DriverProps', 'name f_engine f_tires f_suspensions')


class DriverFacade(Facade):

    def __init__(self):
        self._fwd_prop('dprops', self.logic.dprops)


class Driver(GameObject, DriverFacade):

    def __init__(self, driver_props):
        init_lst = [[('logic', DriverLogic, [self, driver_props])]]
        GameObject.__init__(self, init_lst)
        DriverFacade.__init__(self)
