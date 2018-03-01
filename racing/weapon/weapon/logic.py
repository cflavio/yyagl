from yyagl.gameobject import LogicColleague


class WeaponLogic(LogicColleague):

    def __init__(self, mediator, car, cars, wpn_id):
        LogicColleague.__init__(self, mediator)
        self.car = car
        self.cars = cars
        self.wpn_id = wpn_id
        self.has_fired = False

    def update_props(self, pos, fwd):
        pass

    def fire(self, sfx):
        if sfx: self.mediator.audio.sfx.play()
        self.has_fired = True

    def destroy(self):
        self.car = self.cars = None
        self.notify('on_weapon_destroyed', self.mediator)
        LogicColleague.destroy(self)


class WeaponLogicNetwork(WeaponLogic):

    def update_props(self, pos, fwd):
        if pos == (0, 0, 0) and fwd == (0, 0, 0): return
        self.mediator.gfx.update_props(pos, fwd)

    def update_fired_props(self, pos, fwd):
        if pos == (0, 0, 0) and fwd == (0, 0, 0): return
        self.mediator.gfx.update_fired_props(pos, fwd)
