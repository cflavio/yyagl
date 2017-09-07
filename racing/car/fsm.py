from yyagl.gameobject import Fsm
from yyagl.racing.car.ai import CarResultsAi
from .event import InputBuilder


class CarFsm(Fsm):

    def __init__(self, mdt, car_props):
        Fsm.__init__(self, mdt)
        self.defaultTransitions = {'Loading': ['Countdown'],
                                   'Countdown': ['Play'], 'Play': ['Results']}
        self.cprops = car_props

    def enterResults(self):
        state = self.getCurrentOrNextState()
        has_j = self.mdt.event.props.joystick
        self.mdt.event.input_bld = InputBuilder.create(state, has_j)
        self.mdt.ai.destroy()
        self.mdt.ai = CarResultsAi(self.mdt, self.cprops)
        self.mdt.gui.destroy()
