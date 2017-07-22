from abc import ABCMeta
from yyagl.gameobject import GameObject
from yyagl.facade import Facade
from .logic import TuningLogic
from .gui import TuningGui


class TuningFacade(Facade):

    def __init__(self):
        self._fwd_mth('attach_obs', self.gui.attach)
        self._fwd_mth('detach_obs', self.gui.detach)
        self._fwd_mth('load', self.logic.load)
        self._fwd_mth('to_dct', self.logic.to_dct)
        self._fwd_mth('show_gui', self.gui.show)
        self._fwd_mth('hide_gui', self.gui.hide)
        self._fwd_mth('reset', self.logic.reset)
        self._fwd_prop('car2tuning', self.logic.car2tuning)


class Tuning(GameObject, TuningFacade):
    __metaclass__ = ABCMeta

    def __init__(self, props):
        init_lst = [
            [('gui', TuningGui, [self, props])],
            [('logic', TuningLogic, [self, props.car_names])]]
        GameObject.__init__(self, init_lst)
        TuningFacade.__init__(self)
