from yyagl.gameobject import LogicColleague


class WeaponLogic(LogicColleague):

    def __init__(self, mdt, car, cars):
        LogicColleague.__init__(self, mdt)
        self.car = car
        self.cars = cars
        self.has_fired = False

    def update_props(self, pos, fwd):
        pass

    def fire(self, sfx):
        if sfx: self.mdt.audio.sfx.play()
        self.has_fired = True

    def destroy(self):
        self.car = self.cars = None
        self.notify('on_weapon_destroyed', self.mdt)
        LogicColleague.destroy(self)


class WeaponLogicNetwork(WeaponLogic):

    def update_props(self, pos, fwd):
        if pos == (0, 0, 0) and fwd == (0, 0, 0): return
        self.mdt.gfx.update_props(pos, fwd)

    def update_fired_props(self, pos, fwd):
        if pos == (0, 0, 0) and fwd == (0, 0, 0): return
        self.mdt.gfx.update_fired_props(pos, fwd)
