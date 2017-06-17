from yyagl.gameobject import Fsm
from yyagl.racing.car.ai import CarResultsAi
from .event import InputDctBuilder


class CarFsm(Fsm):

    def __init__(self, mdt, carfsm_props):
        Fsm.__init__(self, mdt)
        self.defaultTransitions = {
            'Loading': ['Countdown'],
            'Countdown': ['Play'],
            'Play': ['Results']}
        self.props = carfsm_props

    def enterResults(self):
        self.mdt.event.input_dct_bld = InputDctBuilder.build(
            self.getCurrentOrNextState(), self.mdt.event.props.joystick)
        self.mdt.ai.destroy()
        self.mdt.ai = CarResultsAi(
            self.mdt, self.props.road_name, self.props.track_waypoints,
            self.props.car_names)
        self.mdt.gui.destroy()
