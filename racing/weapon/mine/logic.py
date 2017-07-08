from yyagl.gameobject import Logic


class MineLogic(Logic):

    def __init__(self, mdt):
        Logic.__init__(self, mdt)
        self.tsk = None

    def fire(self):
        self.mdt.phys.fire()
        self.mdt.audio.sfx.play()
        self.tsk = eng.do_later(20, self.mdt.destroy)

    def destroy(self):
        if self.tsk:
            eng.remove_do_later(self.tsk)
        self.notify('on_weapon_destroyed')
        Logic.destroy(self)
