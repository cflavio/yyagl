from yyagl.gameobject import Logic


class TuningCar(object):

    def __init__(self, f_engine, f_tires, f_suspensions):
        self.f_engine = f_engine
        self.f_tires = f_tires
        self.f_suspensions = f_suspensions


class TuningLogic(Logic):

    def __init__(self, mdt, car_names):
        Logic.__init__(self, mdt)
        self.car_names = car_names
        self.car2tuning = {}
        self.reset()

    def reset(self):
        self.car2tuning = {car: TuningCar(0, 0, 0) for car in self.car_names}

    @property
    def to_dct(self):
        tun = {}
        for car in self.car2tuning:
            tun[car] = {}
            tun[car]['engine'] = self.car2tuning[car].f_engine
            tun[car]['tires'] = self.car2tuning[car].f_tires
            tun[car]['suspensions'] = self.car2tuning[car].f_suspensions
        return tun

    def load(self, tuning_dct):
        self.car2tuning = {}
        for car_name in tuning_dct:
            tun = tuning_dct[car_name]
            new_t = TuningCar(tun.f_engine, tun.f_tires, tun.f_suspensions)
            self.car2tuning[car_name] = new_t
