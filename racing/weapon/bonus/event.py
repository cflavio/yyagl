from yyagl.gameobject import Event


class BonusEvent(Event):

    def __init__(self, mdt):
        Event.__init__(self, mdt)
        self.generate_tsk = None

    def on_collision(self, obj, obj_name):
        is_bon = obj_name == 'Bonus'
        if is_bon and obj in self.mdt.phys.ghost.getOverlappingNodes():
            pos = self.mdt.phys.pos
            game.track.phys.bonuses.remove(self.mdt)
            self.mdt.destroy()
            cre = lambda tsk: game.track.phys.create_bonus(pos)
            self.generate_tsk = taskMgr.doMethodLater(20, cre, 'create bonus')

    def destroy(self):
        Event.destroy(self)
        if self.generate_tsk:
            taskMgr.remove_task(self.generate_tsk)
