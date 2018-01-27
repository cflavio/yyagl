from yyagl.gameobject import FsmColleague
from yyagl.racing.car.ai import CarResultsAi
from .event import InputBuilder


class CarFsm(FsmColleague):

    def __init__(self, mediator, car_props):
        FsmColleague.__init__(self, mediator)
        self.defaultTransitions = {'Loading': ['Countdown'],
                                   'Countdown': ['Play'], 'Play': ['Results']}
        self.cprops = car_props

    def enterPlay(self):
        self.mediator.audio.on_play()

    def enterResults(self):
        state = self.getCurrentOrNextState()
        has_j = self.mediator.event.props.joystick
        self.mediator.event.input_bld = InputBuilder.create(state, has_j)
        self.mediator.ai.destroy()
        self.mediator.ai = CarResultsAi(self.mediator, self.cprops)
        self.mediator.gui.destroy()
