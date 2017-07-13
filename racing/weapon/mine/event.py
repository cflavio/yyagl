from yyagl.gameobject import Event


class MineEvent(Event):

    def __init__(self, mdt, particle_path):
        Event.__init__(self, mdt)
        eng.attach_obs(self.on_collision)
        self.particle_path = particle_path

    def on_collision(self, obj, tgt_obj):
        if tgt_obj.get_name() == self.mdt.phys.minename:
            eng.particle(self.particle_path, render, render, self.mdt.gfx.gfx_np.get_pos(render) + (0, 0, .5), .8)
            self.mdt.destroy()

    def destroy(self):
        eng.detach_obs(self.on_collision)
        Event.destroy(self)
