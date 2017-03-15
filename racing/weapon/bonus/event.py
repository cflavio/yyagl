from yyagl.gameobject import Event


class BonusEvent(Event):

    def __init__(self, mdt):
        Event.__init__(self, mdt)
        self.generate_tsk = None
        eng.attach_obs(self.on_collision)  # facade

    def on_collision(self, obj, obj_name):
        is_bon = obj_name == 'Bonus'
        if is_bon and obj in self.mdt.phys.ghost.getOverlappingNodes():
            self.notify('on_bonus_collected', self.mdt)
            self.mdt.destroy()

    def destroy(self):
        eng.detach_obs(self.on_collision)  # facade
        Event.destroy(self)
