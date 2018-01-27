from yyagl.racing.weapon.weapon.logic import WeaponLogic, WeaponLogicNetwork


class MineLogic(WeaponLogic):

    def __init__(self, mediator, car, cars):
        WeaponLogic.__init__(self, mediator, car, cars)
        self.tsk = None

    def fire(self, sfx):
        WeaponLogic.fire(self, sfx)
        self.mediator.phys.fire()
        self.tsk = self.eng.do_later(30, self.mediator.destroy)

    def destroy(self):
        if self.tsk: self.eng.remove_do_later(self.tsk)
        WeaponLogic.destroy(self)


class MineLogicNetwork(WeaponLogicNetwork, MineLogic): pass
