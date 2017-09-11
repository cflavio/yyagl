from collections import namedtuple
from yyagl.gameobject import GameObject
from yyagl.facade import Facade
from .logic import DriverLogic


DriverInfo = namedtuple('DriverInfo', 'img_idx name speed adherence stability')
DriverProps = namedtuple('DriverProps', 'info car_name f_engine f_tires f_suspensions')


class DriverFacade(Facade):

    def __init__(self):
        self._fwd_prop_lazy('dprops', lambda obj: obj.logic.dprops)


class Driver(GameObject, DriverFacade):

    def __init__(self, driver_props):
        init_lst = [[('logic', DriverLogic, [self, driver_props])]]
        GameObject.__init__(self, init_lst)
        DriverFacade.__init__(self)
