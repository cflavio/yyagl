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

    def __repr__(self):
        return 'driverinfo(%s %s %s %s %s)' % (
            self.img_idx, self.name, self.speed, self.adherence,
            self.stability)

class DriverProps(object):

    def __init__(self, info, car_name, player_idx, f_engine, f_tires, f_suspensions):
        self.info = info
        self.car_name = car_name
        self.player_idx = player_idx
        self.f_engine = f_engine
        self.f_tires = f_tires
        self.f_suspensions = f_suspensions

    def __repr__(self):
        return 'driver(%s %s %s %s %s %s)' % (
            self.info, self.car_name, self.player_idx, self.f_engine,
            self.f_tires, self.f_suspensions)


class DriverFacade(Facade):

    def __init__(self):
        prop_lst = [('dprops', lambda obj: obj.logic.dprops)]
        mth_lst = [('to_dct', lambda obj: obj.logic.to_dct)]
        Facade.__init__(self, prop_lst, mth_lst)


class Driver(GameObject, DriverFacade):

    def __init__(self, driver_props):
        init_lst = [[('logic', DriverLogic, [self, driver_props])]]
        GameObject.__init__(self, init_lst)
        DriverFacade.__init__(self)

    def __repr__(self):
        dpr = self.logic.dprops
        return 'driver(%s %s %s %s %s)' % (
            dpr.info, dpr.car_name, dpr.f_engine, dpr.f_tires,
            dpr.f_suspensions)

    def destroy(self):
        GameObject.destroy(self)
        DriverFacade.destroy(self)
