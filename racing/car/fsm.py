from yyagl.gameobject import Fsm
from yyagl.racing.car.ai import CarResultsAi
from .event import InputDctBuilder


class CarFsm(Fsm):

    def __init__(self, mdt):
        Fsm.__init__(self, mdt)
        self.defaultTransitions = {
            'Loading': ['Countdown'],
            'Countdown': ['Play'],
            'Play': ['Results']}

    def enterResults(self):
        self.mdt.event.input_dct_bld = InputDctBuilder.build(
            self.getCurrentOrNextState(), self.mdt.event.joystick)
        self.mdt.ai.destroy()
        self.mdt.ai = CarResultsAi(self.mdt, self.mdt.road_name)
        self.mdt.gui.destroy()
