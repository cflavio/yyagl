from yyagl.gameobject import GameObject
from yyagl.facade import Facade
from .gfx import BonusGfx
from .phys import BonusPhys
from .event import BonusEvent
from .logic import BonusLogic


class BonusFacade(Facade):

    def __init__(self):
        self._fwd_mth('attach_obs', lambda obj: obj.event.attach)
        self._fwd_mth('detach_obs', lambda obj: obj.event.detach)
        self._fwd_prop('pos', lambda obj: obj.phys.pos)


class Bonus(GameObject, BonusFacade):

    def __init__(self, pos, model_name, model_suff, track_phys, track_gfx):
        init_lst = [
            [('gfx', BonusGfx, [self, pos, model_name, model_suff])],
            [('event', BonusEvent, [self])],
            [('phys', BonusPhys, [self, pos])],
            [('logic', BonusLogic, [self, track_phys, track_gfx])]]
        GameObject.__init__(self, init_lst)
        BonusFacade.__init__(self)

    def destroy(self):
        GameObject.destroy(self)
        BonusFacade.destroy(self)
