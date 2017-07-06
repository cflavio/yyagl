from yyagl.gameobject import Event


class RearRocketEvent(Event):

    def __init__(self, mdt):
        Event.__init__(self, mdt)
        eng.attach_obs(self.on_collision)

    def on_collision(self, obj, obj_name):
        if obj_name == 'RearRocket':
            obj.apply_central_force((0, 0, 200000))
            self.mdt.destroy()
        if obj_name == 'Wall' and obj == self.mdt.phys.node:
            self.mdt.destroy()

    def destroy(self):
        eng.detach_obs(self.on_collision)
        Event.destroy(self)
