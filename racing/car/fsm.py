from yyagl.gameobject import FsmColleague
from yyagl.racing.car.ai import CarResultsAi
from .event import InputBuilder


class CarFsm(FsmColleague):

    def __init__(self, mediator, car_props):
        FsmColleague.__init__(self, mediator)
        self.defaultTransitions = {'Loading': ['Countdown'],
                                   'Countdown': ['Play'],
                                   'Play': ['Waiting', 'Results'],
                                   'Waiting': ['Results']}
        self.cprops = car_props

    def enterPlay(self):
        self.mediator.audio.on_play()

    def enterWaiting(self):
        state = self.getCurrentOrNextState()
        #self.mediator.event.input_bld = InputBuilder.create(state, has_j)
        self.mediator.ai.destroy()
        self.mediator.ai = CarResultsAi(self.mediator, self.cprops)
        self.mediator.gui.hide()
        #self.mediator.gui.panel.enter_waiting()


class CarPlayerFsm(CarFsm):

    def enterWaiting(self):
        CarFsm.enterWaiting(self)
        self.mediator.gui.panel.enter_waiting()

    def enterResults(self):
        self.mediator.gui.panel.exit_waiting()
