from yyagl.gameobject import GameObject
from yyagl.facade import Facade
from .gfx import BonusGfx
from .phys import BonusPhys
from .event import BonusEvent
from .logic import BonusLogic


class BonusFacade(Facade):

    def __init__(self):
        prop_lst = [('pos', lambda obj: obj.phys.pos)]
        mth_lst = [
            ('attach_obs', lambda obj: obj.event.attach),
            ('detach_obs', lambda obj: obj.event.detach)]
        Facade.__init__(self, prop_lst, mth_lst)



class Bonus(GameObject, BonusFacade):

    def __init__(self, pos, model_name, model_suff, track_phys, track_gfx):
        GameObject.__init__(self)
        self.gfx = BonusGfx(self, pos, model_name, model_suff)
        self.event = BonusEvent(self)
        self.phys = BonusPhys(self, pos)
        self.logic = BonusLogic(self, track_phys, track_gfx)
        BonusFacade.__init__(self)

    def destroy(self):
        self.gfx.destroy()
        self.event.destroy()
        self.phys.destroy()
        self.logic.destroy()
        GameObject.destroy(self)
        BonusFacade.destroy(self)
