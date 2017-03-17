from abc import ABCMeta
from yyagl.gameobject import GameObjectMdt
from .logic import TuningLogic
from .gui import TuningGui, TuningGuiProps


class TuningProps(object):

    def __init__(
            self, cars, player_car, background, engine_img, tires_img,
            suspensions_img):
        self.cars = cars
        self.player_car = player_car
        self.background = background
        self.engine_img = engine_img
        self.tires_img = tires_img
        self.suspensions_img = suspensions_img


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
        tuninggui_props = TuningGuiProps(
            t_p.player_car, t_p.background, t_p.engine_img, t_p.tires_img,
            t_p.suspensions_img)
        init_lst = [
            [('gui', TuningGui, [self, tuninggui_props])],
            [('logic', TuningLogic, [self, t_p.cars])]]
        GameObjectMdt.__init__(self, init_lst)
