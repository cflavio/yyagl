from yyagl.gameobject import Logic


class DriverLogic(Logic):

    def __init__(self, mdt, driver_props):
        Logic.__init__(self, mdt)
        self.dprops = driver_props
