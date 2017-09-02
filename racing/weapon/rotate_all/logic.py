from yyagl.racing.weapon.weapon.logic import WeaponLogic


class RotateAllLogic(WeaponLogic):

    def fire(self):
        WeaponLogic.fire(self)
        self.notify('on_rotate_all', self.car)
        self.mdt.destroy()
