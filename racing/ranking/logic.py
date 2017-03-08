from yyagl.gameobject import Logic


class RankingLogic(Logic):

    def __init__(self, mdt, cars):
        Logic.__init__(self, mdt)
        self.ranking = {}
        self.cars = cars
        self.reset()

    def reset(self):
        self.ranking = {car: 0 for car in self.cars}

    def load(self, ranking):
        self.ranking = ranking
