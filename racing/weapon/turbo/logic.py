from yyagl.gameobject import Logic


class TurboLogic(Logic):

    def __init__(self, mdt, car):
        Logic.__init__(self, mdt)
        self.car = car
        self.stored_max_speed = self.stored_engine_acc_frc = \
            self.destroy_tsk = None
        self.has_fired = False

    def fire(self):
        self.mdt.audio.sfx.play()
        self.stored_max_speed = self.car.phys.max_speed
        self.stored_engine_acc_frc = self.car.phys.engine_acc_frc
        self.car.phys.max_speed *= 1.5
        self.car.phys.engine_acc_frc *= 1.5
        self.destroy_tsk = eng.do_later(5, self.mdt.destroy)
        self.has_fired = True

    def destroy(self):
        if self.stored_max_speed is not None:
            self.car.phys.max_speed = self.stored_max_speed
        if self.stored_engine_acc_frc is not None:
            self.car.phys.engine_acc_frc = self.stored_engine_acc_frc
        if self.stored_engine_acc_frc is not None:
            eng.remove_do_later(self.destroy_tsk)
        self.notify('on_weapon_destroyed')
        self.car = None
        Logic.destroy(self)
