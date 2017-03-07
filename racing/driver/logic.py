from yyagl.gameobject import Logic


class DriverLogic(Logic):

    def __init__(self, mdt, name, engine, tires, suspensions):
        Logic.__init__(self, mdt)
        self.name = name
        self.engine = engine
        self.tires = tires
        self.suspensions = suspensions
