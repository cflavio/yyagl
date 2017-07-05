from yyagl.gameobject import Event


class MineEvent(Event):

    def __init__(self, mdt):
        Event.__init__(self, mdt)
        eng.attach_obs(self.on_collision)

    def on_collision(self, obj, obj_name):
        if obj_name == self.mdt.phys.minename:
            self.mdt.destroy()

    def destroy(self):
        eng.detach_obs(self.on_collision)
        Event.destroy(self)
