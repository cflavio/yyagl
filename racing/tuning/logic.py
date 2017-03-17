from yyagl.gameobject import Logic


class TuningCar(object):

    def __init__(self, engine, tires, suspensions):
        self.engine = engine
        self.tires = tires
        self.suspensions = suspensions


class TuningLogic(Logic):

    def __init__(self, mdt, cars):
        Logic.__init__(self, mdt)
        self.cars = cars
        self.tunings = {}
        self.reset()

    def reset(self):
        self.tunings = {car: TuningCar(0, 0, 0) for car in self.cars}

    def to_dct(self):
        tun = {}
        for car in self.tunings:
            c_t = self.tunings[car]
            tun[car] = {}
            tun[car]['engine'] = c_t.engine
            tun[car]['tires'] = c_t.tires
            tun[car]['suspensions'] = c_t.suspensions
        return tun

    def load(self, tuning):
        self.tunings = {}
        for car in tuning:
            c_t = tuning[car]
            new_t = TuningCar(
                c_t['engine'], c_t['tires'], c_t['suspensions'])
            self.tunings[car] = new_t
