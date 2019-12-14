class TuningPlayer:

    def __init__(self, engine, tires, suspensions):
        self.engine = engine
        self.tires = tires
        self.suspensions = suspensions

    def __repr__(self):
        return 'tuning(%s %s %s)' % (
            self.engine, self.tires, self.suspensions)


class Player:

    human, ai, network = range(3)

    def __init__(self, driver=None, car=None, kind=None, tuning=None, human_idx=None, name='', points=0):
        self.driver = driver
        self.car = car
        self.kind = kind
        self.tuning = tuning
        self.human_idx = human_idx
        self.name = name
        self.points = points

    def __repr__(self):
        return 'player(%s %s %s %s %s %s)' % (
            self.driver, self.car, self.kind, self.tuning, self.human_idx, self.name)
