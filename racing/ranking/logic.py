from yyagl.gameobject import Logic


class RankingLogic(Logic):

    def __init__(self, mdt, car_names):
        Logic.__init__(self, mdt)
        self.carname2points = {}
        self.car_names = car_names
        self.reset()

    def reset(self):
        self.carname2points = {car: 0 for car in self.car_names}

    def load(self, carname2points):
        self.carname2points = carname2points
