from yyagl.gameobject import Logic


class TurboLogic(Logic):

    def __init__(self, mdt, car):
        Logic.__init__(self, mdt)
        self.car = car

    def fire(self):
        self.mdt.audio.sfx.play()
        self.stored_max_speed = self.car.phys.max_speed
        self.stored_engine_acc_frc = self.car.phys.engine_acc_frc
        self.car.phys.max_speed *= 1.5
        self.car.phys.engine_acc_frc *= 1.5
        eng.do_later(5, self.mdt.destroy)

    def destroy(self):
        self.car.phys.max_speed = self.stored_max_speed 
        self.car.phys.engine_acc_frc = self.stored_engine_acc_frc
        self.notify('on_weapon_destroyed')
        self.car = None
        Logic.destroy(self)
