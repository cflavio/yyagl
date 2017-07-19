from yyagl.gameobject import Logic


class TuningCar(object):

    def __init__(self, engine_val, tires_val, suspensions_val):
        self.engine = engine_val
        self.tires = tires_val
        self.suspensions = suspensions_val


class TuningLogic(Logic):

    def __init__(self, mdt, car_names):
        Logic.__init__(self, mdt)
        self.car_names = car_names
        self.car2tuning = {}
        self.reset()

    def reset(self):
        self.car2tuning = {car: TuningCar(0, 0, 0) for car in self.car_names}

    def to_dct(self):
        tun = {}
        for car in self.car2tuning:
            tun[car] = {}
            tun[car]['engine'] = self.car2tuning[car].engine
            tun[car]['tires'] = self.car2tuning[car].tires
            tun[car]['suspensions'] = self.car2tuning[car].suspensions
        return tun

    def load(self, tuning_dct):
        self.car2tuning = {}
        for car_name in tuning_dct:
            tun = tuning_dct[car_name]
            new_t = TuningCar(
                tun['engine'], tun['tires'], tun['suspensions'])
            self.car2tuning[car_name] = new_t
