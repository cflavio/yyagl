from yyagl.gameobject import Logic


class RocketLogic(Logic):

    def fire(self):
        self.mdt.phys.fire()
        self.mdt.audio.sfx.play()
        taskMgr.doMethodLater(5, lambda tsk: self.mdt.destroy(), 'rocket')

    def destroy(self):
        self.mdt.car.logic.weapon = None
        Logic.destroy(self)
