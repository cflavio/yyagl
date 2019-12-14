from abc import ABCMeta
from yyagl.gameobject import GameObject
from yyagl.facade import Facade
from .gui import TuningGui


class TuningFacade(Facade):

    def __init__(self):
        prop_lst = []  # [('car2tuning', lambda obj: obj.logic.car2tuning),
        #            ('to_dct', lambda obj: obj.logic.to_dct)]
        mth_lst = [
            ('attach_obs', lambda obj: obj.gui.attach),
            ('detach_obs', lambda obj: obj.gui.detach),
            #('load', lambda obj: obj.logic.load),
            ('show_gui', lambda obj: obj.gui.show),
            ('hide_gui', lambda obj: obj.gui.hide)]
        Facade.__init__(self, prop_lst, mth_lst)


class Tuning(GameObject, TuningFacade):
    __metaclass__ = ABCMeta

    def __init__(self, props):
        GameObject.__init__(self)
        self.gui = TuningGui(self, props)
        TuningFacade.__init__(self)

    def destroy(self):
        self.gui.destroy()
        GameObject.destroy(self)
        TuningFacade.destroy(self)
