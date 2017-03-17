from abc import ABCMeta
from yyagl.gameobject import GameObjectMdt
from .logic import RankingLogic
from .gui import RankingGui


class RankingFacade(object):

    def load(self, ranking):
        return self.logic.load(ranking)


class Ranking(GameObjectMdt, RankingFacade):
    __metaclass__ = ABCMeta

    def __init__(self, cars, background, font, fg_col):
        init_lst = [
            [('gui', RankingGui, [self, background, font, fg_col])],
            [('logic', RankingLogic, [self, cars])]]
        GameObjectMdt.__init__(self, init_lst)
