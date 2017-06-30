from yyagl.gameobject import Logic


class RotateAllLogic(Logic):

    def __init__(self, mdt, car, cars):
        Logic.__init__(self, mdt)
        self.car = car
        self.cars = cars

    def fire(self):
        self.mdt.audio.sfx.play()
        self.cars = [car for car in self.cars if car.name != self.car.name]
        map(lambda car: car.phys.rotate(), self.cars)
        self.mdt.destroy()

    def destroy(self):
        self.notify('on_weapon_destroyed')
        self.car = self.cars = None
        Logic.destroy(self)
