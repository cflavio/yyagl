from yyagl.racing.weapon.weapon.logic import WeaponLogic


class TurboLogic(WeaponLogic):

    def __init__(self, mdt, car, cars):
        WeaponLogic.__init__(self, mdt, car, cars)
        self.stored_max_speed = self.stored_engine_acc_frc = \
            self.destroy_tsk = None

    def fire(self):
        WeaponLogic.fire(self)
        self.stored_max_speed = self.car.phys.max_speed
        self.stored_engine_acc_frc = self.car.phys.engine_acc_frc
        self.car.phys.max_speed *= 1.5
        self.car.phys.engine_acc_frc *= 1.5
        self.destroy_tsk = self.eng.do_later(5, self.mdt.destroy)

    def destroy(self):
        if self.stored_max_speed is not None:
            self.car.phys.max_speed = self.stored_max_speed
        if self.stored_engine_acc_frc is not None:
            self.car.phys.engine_acc_frc = self.stored_engine_acc_frc
        if self.stored_engine_acc_frc is not None:
            self.eng.remove_do_later(self.destroy_tsk)
        WeaponLogic.destroy(self)
