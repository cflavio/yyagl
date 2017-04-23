from abc import ABCMeta
from yyagl.gameobject import GameObject
from .logic import RankingLogic
from .gui import RankingGui


class RankingFacade(object):

    def load(self, ranking):
        return self.logic.load(ranking)

    @property
    def ranking(self):
        return self.logic.ranking

    def show(self):
        return self.gui.show()

    def hide(self):
        return self.gui.hide()


class Ranking(GameObject, RankingFacade):
    __metaclass__ = ABCMeta

    def __init__(self, cars, background, font, fg_col):
        init_lst = [
            [('gui', RankingGui, [self, background, font, fg_col])],
            [('logic', RankingLogic, [self, cars])]]
        GameObject.__init__(self, init_lst)
