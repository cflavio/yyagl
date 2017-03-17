from yyagl.gameobject import Logic


class DriverLogic(Logic):

    def __init__(self, mdt, driver_props):
        Logic.__init__(self, mdt)
        self.name = driver_props.name
        self.engine = driver_props.engine
        self.tires = driver_props.tires
        self.suspensions = driver_props.suspensions
