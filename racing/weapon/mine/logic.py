from yyagl.racing.weapon.weapon.logic import WeaponLogic, WeaponLogicNetwork


class MineLogic(WeaponLogic):

    def __init__(self, mediator, car, cars, wpn_id):
        WeaponLogic.__init__(self, mediator, car, cars, wpn_id)
        self.tsk = None

    def fire(self, sfx):
        WeaponLogic.fire(self, sfx)
        self.mediator.phys.fire()
        self.tsk = self.eng.do_later(30, self.mediator.destroy)

    def destroy(self):
        if self.tsk: self.eng.rm_do_later(self.tsk)
        WeaponLogic.destroy(self)


class MineLogicNetwork(WeaponLogicNetwork, MineLogic): pass
