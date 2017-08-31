from yyagl.gameobject import Logic


class RotateAllLogic(Logic):

    def __init__(self, mdt, car, cars):
        Logic.__init__(self, mdt)
        self.car = car
        self.cars = cars
        self.has_fired = False

    def fire(self):
        self.mdt.audio.sfx.play()
        self.notify('on_rotate_all', self.car)
        self.has_fired = True
        self.mdt.destroy()

    def destroy(self):
        self.notify('on_weapon_destroyed')
        self.car = self.cars = None
        Logic.destroy(self)
