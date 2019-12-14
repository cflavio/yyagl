from abc import ABCMeta
from yyagl.gameobject import GameObject
from yyagl.facade import Facade
#from .logic import RankingLogic
from .gui import RankingGui


class RankingFacade(Facade):

    def __init__(self):
        prop_lst = []  # [('carname2points', lambda obj: obj.logic.carname2points)]
        mth_lst = [
            #('load', lambda obj: obj.logic.load),
            ('show', lambda obj: obj.gui.show),
            ('hide', lambda obj: obj.gui.hide),
            #('reset', lambda obj: obj.logic.reset),
            ('attach_obs', lambda obj: obj.gui.attach_obs),
            ('detach_obs', lambda obj: obj.gui.detach_obs)]
        Facade.__init__(self, prop_lst, mth_lst)


class Ranking(GameObject, RankingFacade):
    __metaclass__ = ABCMeta

    def __init__(self, car_names, background_fpath, font, fg_col):
        GameObject.__init__(self)
        self.gui = RankingGui(self, background_fpath, font, fg_col)
        #self.logic = RankingLogic(self, car_names)
        RankingFacade.__init__(self)

    def destroy(self):
        self.gui.destroy()
        #self.logic.destroy()
        GameObject.destroy(self)
        RankingFacade.destroy(self)
