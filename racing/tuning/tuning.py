from abc import ABCMeta
from yyagl.gameobject import GameObject
from yyagl.facade import Facade
from .logic import TuningLogic
from .gui import TuningGui


class TuningFacade(Facade):

    def __init__(self):
        self._fwd_mth('attach_obs', lambda obj: obj.gui.attach)
        self._fwd_mth('detach_obs', lambda obj: obj.gui.detach)
        self._fwd_mth('load', lambda obj: obj.logic.load)
        self._fwd_mth('show_gui', lambda obj: obj.gui.show)
        self._fwd_mth('hide_gui', lambda obj: obj.gui.hide)
        self._fwd_mth('reset', lambda obj: obj.logic.reset)
        self._fwd_prop('to_dct', lambda obj: obj.logic.to_dct)
        self._fwd_prop('car2tuning', lambda obj: obj.logic.car2tuning)


class Tuning(GameObject, TuningFacade):
    __metaclass__ = ABCMeta

    def __init__(self, props):
        init_lst = [
            [('gui', TuningGui, [self, props])],
            [('logic', TuningLogic, [self, props.car_names])]]
        GameObject.__init__(self, init_lst)
        TuningFacade.__init__(self)

    def destroy(self):
        GameObject.destroy(self)
        TuningFacade.destroy(self)
