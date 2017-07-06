from yyagl.gameobject import Logic


class RearRocketLogic(Logic):

    def __init__(self, mdt):
        Logic.__init__(self, mdt)
        self.tsk = None

    def fire(self):
        self.mdt.phys.fire()
        self.mdt.audio.sfx.play()
        self.tsk = eng.do_later(10, self.mdt.destroy)

    def destroy(self):
        eng.remove_do_later(self.tsk)
        self.notify('on_weapon_destroyed')
        Logic.destroy(self)
