from yyagl.gameobject import Logic


class MineLogic(Logic):

    def fire(self):
        self.mdt.phys.fire()
        self.mdt.audio.sfx.play()
        eng.do_later(20, self.mdt.destroy)

    def destroy(self):
        self.notify('on_weapon_destroyed')
        Logic.destroy(self)
