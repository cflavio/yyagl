from yyagl.racing.weapon.weapon.logic import WeaponLogic


class RotateAllLogic(WeaponLogic):

    def fire(self, sfx):
        WeaponLogic.fire(self, sfx)
        self.notify('on_rotate_all', self.car)
        self.mediator.destroy()
