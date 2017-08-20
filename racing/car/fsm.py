from yyagl.gameobject import Fsm
from yyagl.racing.car.ai import CarResultsAi
from .event import InputDctBuilder


class CarFsm(Fsm):

    def __init__(self, mdt, car_props, race_props):
        Fsm.__init__(self, mdt)
        self.defaultTransitions = {
            'Loading': ['Countdown'],
            'Countdown': ['Play'],
            'Play': ['Results']}
        self.cprops = car_props
        self.rprops = race_props

    def enterResults(self):
        self.mdt.event.input_dct_bld = InputDctBuilder.build(
            self.getCurrentOrNextState(), self.mdt.event.props.joystick)
        self.mdt.ai.destroy()
        self.mdt.ai = CarResultsAi(
            self.mdt, self.rprops.road_name, self.cprops.track_waypoints,
            self.rprops.cars, self.cprops.name)
        self.mdt.gui.destroy()
