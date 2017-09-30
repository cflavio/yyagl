from yyagl.gameobject import Logic


class WeaponLogic(Logic):

    def __init__(self, mdt, car, cars):
        Logic.__init__(self, mdt)
        self.car = car
        self.cars = cars
        self.has_fired = False

    def fire(self, sfx):
        if sfx: self.mdt.audio.sfx.play()
        self.has_fired = True

    def destroy(self):
        self.car = self.cars = None
        self.notify('on_weapon_destroyed')
        Logic.destroy(self)
