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

    def __init__(self, pos, model_name, model_suff, waypoints):
        init_lst = [
            [('gfx', BonusGfx, [self, pos, model_name, model_suff])],
            [('event', BonusEvent, [self])],
            [('phys', BonusPhys, [self, pos])],
            [('logic', BonusLogic, [self, waypoints])]]
        GameObject.__init__(self, init_lst)
