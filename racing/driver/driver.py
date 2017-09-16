from collections import namedtuple
from yyagl.gameobject import GameObject
from yyagl.facade import Facade
from .logic import DriverLogic


DriverInfo = namedtuple('DriverInfo', 'img_idx name speed adherence stability')
__fields = 'info car_name f_engine f_tires f_suspensions'
DriverProps = namedtuple('DriverProps', __fields)


class DriverFacade(Facade):

    def __init__(self):
        self._fwd_prop_lazy('dprops', lambda obj: obj.logic.dprops)
        self._fwd_mth_lazy('to_dct', lambda obj: obj.logic.to_dct)


class Driver(GameObject, DriverFacade):

    def __init__(self, driver_props):
        init_lst = [[('logic', DriverLogic, [self, driver_props])]]
        GameObject.__init__(self, init_lst)
        DriverFacade.__init__(self)

    def destroy(self):
        GameObject.destroy(self)
        DriverFacade.destroy(self)
