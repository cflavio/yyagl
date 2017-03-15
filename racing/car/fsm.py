from yyagl.gameobject import Fsm
from yyagl.racing.car.ai import CarResultsAi
from .event import InputDctBuilder


class CarFsmProps(object):

    def __init__(self, road_name, waypoints):
        self.road_name = road_name
        self.waypoints = waypoints


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
        self.mdt.ai = CarResultsAi(self.mdt, self.props.road_name,
                                   self.props.waypoints)
        self.mdt.gui.destroy()
