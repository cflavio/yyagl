from yyagl.racing.weapon.weapon.logic import WeaponLogic


class MineLogic(WeaponLogic):

    def __init__(self, mdt, car, cars):
        WeaponLogic.__init__(self, mdt, car, cars)
        self.tsk = None

    def fire(self):
        WeaponLogic.fire(self)
        self.mdt.phys.fire()
        self.tsk = eng.do_later(30, self.mdt.destroy)

    def destroy(self):
        if self.tsk: eng.remove_do_later(self.tsk)
        WeaponLogic.destroy(self)
