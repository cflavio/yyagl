from abc import ABCMeta
from yyagl.gameobject import GameObjectMdt
from .logic import RankingLogic
from .gui import RankingGui


class Ranking(GameObjectMdt):
    __metaclass__ = ABCMeta
    logic_cls = RankingLogic
    gui_cls = RankingGui

    def __init__(self, init_lst=[]):
        init_lst = [
            [('gui', self.gui_cls, [self])],
            [('logic', self.logic_cls, [self])]]
        GameObjectMdt.__init__(self, init_lst)
