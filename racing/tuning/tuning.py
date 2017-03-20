from abc import ABCMeta
from yyagl.gameobject import GameObjectMdt
from .logic import TuningLogic
from .gui import TuningGui, TuningGuiProps


class TuningProps(object):

    def __init__(
            self, cars, player_car, background, tuning_imgs):
        self.cars = cars
        self.player_car = player_car
        self.background = background
        self.tuning_imgs = tuning_imgs


class TuningFacade(object):

    def attach_obs(self, meth):
        return self.gui.attach(meth)

    def detach_obs(self, meth):
        return self.gui.detach(meth)

    def load(self, ranking):
        return self.logic.load(ranking)


class Tuning(GameObjectMdt, TuningFacade):
    __metaclass__ = ABCMeta

    def __init__(self, tuning_props):
        t_p = tuning_props
        tuninggui_props = TuningGuiProps(t_p.player_car, t_p.background,
                                         t_p.tuning_imgs)
        init_lst = [
            [('gui', TuningGui, [self, tuninggui_props])],
            [('logic', TuningLogic, [self, t_p.cars])]]
        GameObjectMdt.__init__(self, init_lst)
