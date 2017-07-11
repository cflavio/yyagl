from yyagl.gameobject import Logic


class MineLogic(Logic):

    def __init__(self, mdt):
        Logic.__init__(self, mdt)
        self.tsk = None
        self.has_fired = False

    def fire(self):
        self.mdt.phys.fire()
        self.mdt.audio.sfx.play()
        self.tsk = eng.do_later(20, self.mdt.destroy)
        self.has_fired = True

    def destroy(self):
        if self.tsk:
            eng.remove_do_later(self.tsk)
        self.notify('on_weapon_destroyed')
        Logic.destroy(self)
