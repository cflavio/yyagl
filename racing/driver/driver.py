from yyagl.gameobject import GameObject
from yyagl.facade import Facade
from .logic import DriverLogic


class DriverInfo(object):

    def __init__(self, img_idx, name, speed, adherence, stability):
        self.img_idx = img_idx
        self.name = name
        self.speed = speed
        self.adherence = adherence
        self.stability = stability

class DriverProps(object):

    def __init__(self, info, car_name, f_engine, f_tires, f_suspensions):
        self.info = info
        self.car_name = car_name
        self.f_engine = f_engine
        self.f_tires = f_tires
        self.f_suspensions = f_suspensions



class DriverFacade(Facade):

    def __init__(self):
        self._fwd_prop('dprops', lambda obj: obj.logic.dprops)
        self._fwd_mth('to_dct', lambda obj: obj.logic.to_dct)


class Driver(GameObject, DriverFacade):

    def __init__(self, driver_props):
        init_lst = [[('logic', DriverLogic, [self, driver_props])]]
        GameObject.__init__(self, init_lst)
        DriverFacade.__init__(self)

    def destroy(self):
        GameObject.destroy(self)
        DriverFacade.destroy(self)
