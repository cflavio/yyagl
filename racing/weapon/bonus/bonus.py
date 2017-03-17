from yyagl.gameobject import GameObjectMdt
from .gfx import BonusGfx
from .phys import BonusPhys
from .event import BonusEvent


class BonusFacade(object):

    def attach_obs(self, meth):
        return self.event.attach(meth)

    def detach_obs(self, meth):
        return self.event.detach(meth)

    @property
    def pos(self):
        return self.phys.pos


class Bonus(GameObjectMdt, BonusFacade):
    gfx_cls = BonusGfx
    phys_cls = BonusPhys
    event_cls = BonusEvent

    def __init__(self, pos, model_name, model_suff):
        init_lst = [
            [('gfx', self.gfx_cls, [self, pos, model_name, model_suff])],
            [('event', self.event_cls, [self])],
            [('phys', self.phys_cls, [self, pos])]]
        GameObjectMdt.__init__(self, init_lst)
