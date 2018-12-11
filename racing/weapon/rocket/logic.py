from math import pi
from yyagl.racing.weapon.weapon.logic import WeaponLogic, WeaponLogicNetwork
from yyagl.engine.vec import Vec


class RocketLogic(WeaponLogic):

    def __init__(self, mediator, car, cars, wpn_id):
        WeaponLogic.__init__(self, mediator, car, cars, wpn_id)
        self.tsk = None
        self.particle = None

    def fire(self, sfx):
        WeaponLogic.fire(self, sfx)
        self.mediator.phys.fire()
        self.tsk = self.eng.do_later(10, self.mediator.destroy)
        self.particle = self.eng.particle(self.mediator.gfx.gfx_np,
                                          'dust', 10000, (.9, .7, .2, .6), pi/20, .1, .001, 0, vel=3, part_lifetime=1.2)

    def destroy(self):
        if self.particle: self.particle.destroy()
        if self.tsk: self.eng.rm_do_later(self.tsk)
        WeaponLogic.destroy(self)


class RocketLogicNetwork(WeaponLogicNetwork, RocketLogic): pass
