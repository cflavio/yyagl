from yyagl.gameobject import GameObject
from .gfx import BonusGfx
from .phys import BonusPhys
from .event import BonusEvent
from .logic import BonusLogic


class BonusFacade(object):

    def attach_obs(self, meth):
        return self.event.attach(meth)

    def detach_obs(self, meth):
        return self.event.detach(meth)

    @property
    def pos(self):
        return self.phys.pos


class Bonus(GameObject, BonusFacade):
    gfx_cls = BonusGfx
    phys_cls = BonusPhys
    event_cls = BonusEvent
    logic_cls = BonusLogic

    def __init__(self, pos, model_name, model_suff, waypoints):
        init_lst = [
            [('gfx', self.gfx_cls, [self, pos, model_name, model_suff])],
            [('event', self.event_cls, [self])],
            [('phys', self.phys_cls, [self, pos])],
            [('logic', self.logic_cls, [self, waypoints])]]
        GameObject.__init__(self, init_lst)
