from yyagl.gameobject import Event


class RocketEvent(Event):

    def __init__(self, mdt, particle_path):
        Event.__init__(self, mdt)
        eng.attach_obs(self.on_collision)
        self.particle_path = particle_path

    def on_collision(self, obj, tgt_obj):
        if tgt_obj.get_name() == 'Rocket' and tgt_obj == self.mdt.phys.phys_node:
            obj.apply_central_force((0, 0, 200000))
            eng.particle(self.particle_path, render, render, self.mdt.gfx.gfx_np.get_pos(render) + (0, 0, .5), .8)
            self.mdt.destroy()
        if tgt_obj.get_name() == 'Wall' and obj == self.mdt.phys.phys_node:
            self.mdt.destroy()

    def destroy(self):
        eng.detach_obs(self.on_collision)
        Event.destroy(self)
