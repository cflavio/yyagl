from yyagl.gameobject import Event


class WeaponEvent(Event):

    def __init__(self, mdt, particle_path):
        Event.__init__(self, mdt)
        self.eng.attach_obs(self.on_collision)
        self.particle_path = particle_path

    def _on_coll_success(self):
        pos = self.mdt.gfx.gfx_np.get_pos(render) + (0, 0, .5)
        self.eng.particle(render, pos, (0, 0, 0), (1, .4, .1, 1), .8)
        self.mdt.destroy()

    def _eval_wall_coll(self, tgt_obj, obj):
        if tgt_obj.get_name() == 'Wall' and obj == self.mdt.phys.node:
            self.mdt.destroy()

    def destroy(self):
        self.eng.detach_obs(self.on_collision)
        Event.destroy(self)


class RocketWeaponEvent(WeaponEvent):

    def on_collision(self, obj, tgt_obj):
        pnode = self.mdt.phys.node
        if tgt_obj.get_name() == self.wpn_name and tgt_obj == pnode:
            obj.apply_central_force((0, 0, 30000))
            self.mdt.logic.notify('on_hit', obj)
            self._on_coll_success()
        self._eval_wall_coll(tgt_obj, obj)
