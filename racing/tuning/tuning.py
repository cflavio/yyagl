from abc import ABCMeta
from yyagl.gameobject import GameObjectMdt
from .logic import TuningLogic
from .gui import TuningGui


class Tuning(GameObjectMdt):
    __metaclass__ = ABCMeta
    logic_cls = TuningLogic
    gui_cls = TuningGui

    def __init__(self, init_lst=[]):
        init_lst = [
            [('gui', self.gui_cls, [self])],
            [('logic', self.logic_cls, [self])]]
        GameObjectMdt.__init__(self, init_lst)
