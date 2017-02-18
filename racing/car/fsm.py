from yyagl.gameobject import Fsm
from yyagl.racing.car.ai import CarResultsAi


class CarFsm(Fsm):

    def __init__(self, mdt):
        Fsm.__init__(self, mdt)
        self.defaultTransitions = {
            'Loading': ['Countdown'],
            'Countdown': ['Play'],
            'Play': ['Results']}

    def enterResults(self):
        self.mdt.ai.destroy()
        self.mdt.ai = CarResultsAi(self.mdt)
        self.mdt.gui.destroy()
