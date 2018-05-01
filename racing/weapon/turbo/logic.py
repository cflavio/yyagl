from yyagl.racing.weapon.weapon.logic import WeaponLogic, WeaponLogicNetwork


class TurboLogic(WeaponLogic):

    def __init__(self, mediator, car, cars, wpn_id):
        WeaponLogic.__init__(self, mediator, car, cars, wpn_id)
        self.stored_max_speed = self.stored_engine_acc_frc = \
            self.destroy_tsk = None

    def fire(self, sfx):
        WeaponLogic.fire(self, sfx)
        self.stored_max_speed = self.car.phys.max_speed
        self.stored_engine_acc_frc = self.car.phys.engine_acc_frc
        self.car.phys.max_speed *= 1.5
        self.car.phys.engine_acc_frc *= 1.5
        self.destroy_tsk = self.eng.do_later(5, self.mediator.destroy)

    def destroy(self):
        if self.stored_max_speed is not None:
            self.car.phys.max_speed = self.stored_max_speed
        if self.stored_engine_acc_frc is not None:
            self.car.phys.engine_acc_frc = self.stored_engine_acc_frc
        if self.stored_engine_acc_frc is not None:
            self.eng.rm_do_later(self.destroy_tsk)
        WeaponLogic.destroy(self)


class TurboLogicNetwork(WeaponLogicNetwork, TurboLogic): pass
