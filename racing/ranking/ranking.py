from abc import ABCMeta
from yyagl.gameobject import GameObjectMdt
from .logic import RankingLogic
from .gui import RankingGui


class Ranking(GameObjectMdt):
    __metaclass__ = ABCMeta

    def __init__(self, cars, background, font):
        init_lst = [
            [('gui', RankingGui, [self, background, font])],
            [('logic', RankingLogic, [self, cars])]]
        GameObjectMdt.__init__(self, init_lst)
