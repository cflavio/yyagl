from yyagl.racing.weapon.weapon.logic import WeaponLogic, WeaponLogicNetwork


class RocketLogic(WeaponLogic):

    def __init__(self, mediator, car, cars, wpn_id):
        WeaponLogic.__init__(self, mediator, car, cars, wpn_id)
        self.tsk = None

    def fire(self, sfx):
        WeaponLogic.fire(self, sfx)
        self.mediator.phys.fire()
        self.tsk = self.eng.do_later(10, self.mediator.destroy)

    def destroy(self):
        if self.tsk: self.eng.remove_do_later(self.tsk)
        WeaponLogic.destroy(self)


class RocketLogicNetwork(WeaponLogicNetwork, RocketLogic): pass
