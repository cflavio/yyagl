from yyagl.gameobject import Logic


class RocketLogic(Logic):

    def fire(self):
        self.mdt.phys.fire()
        self.mdt.audio.sfx.play()
        eng.do_later(5, self.mdt.destroy)

    def destroy(self):
        self.notify('on_weapon_destroyed')
        Logic.destroy(self)
