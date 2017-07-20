from abc import ABCMeta
from yyagl.gameobject import GameObject
from .logic import RankingLogic
from .gui import RankingGui


class RankingFacade(object):

    def load(self, ranking):
        return self.logic.load(ranking)

    @property
    def carname2points(self):
        return self.logic.carname2points

    def show(self):
        return self.gui.show()

    def hide(self):
        return self.gui.hide()

    def reset(self):
        return self.logic.reset()


class Ranking(GameObject, RankingFacade):
    __metaclass__ = ABCMeta

    def __init__(self, car_names, background_fpath, font, fg_col):
        init_lst = [
            [('gui', RankingGui, [self, background_fpath, font, fg_col])],
            [('logic', RankingLogic, [self, car_names])]]
        GameObject.__init__(self, init_lst)
