from yyagl.gameobject import GameObject
from yyagl.facade import Facade
from .gfx import BonusGfx
from .phys import BonusPhys
from .event import BonusEvent
from .logic import BonusLogic


class BonusFacade(Facade):

    def __init__(self):
        self._fwd_mth('attach_obs', self.event.attach)
        self._fwd_mth('detach_obs', self.event.detach)
        self._fwd_prop('pos', self.phys.pos)


class Bonus(GameObject, BonusFacade):

    def __init__(self, pos, model_name, model_suff, waypoints):
        init_lst = [
            [('gfx', BonusGfx, [self, pos, model_name, model_suff])],
            [('event', BonusEvent, [self])],
            [('phys', BonusPhys, [self, pos])],
            [('logic', BonusLogic, [self, waypoints])]]
        GameObject.__init__(self, init_lst)
        BonusFacade.__init__(self)

    def destroy(self):
        GameObject.destroy(self)
        BonusFacade.destroy(self)
