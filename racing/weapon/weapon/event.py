from random import choice
from yyagl.gameobject import EventColleague


class WeaponEvent(EventColleague):

    def __init__(self, mdt, particle_path):
        EventColleague.__init__(self, mdt)
        self.eng.attach_obs(self.on_collision)
        self.particle_path = particle_path

    def _on_coll_success(self):
        pos = self.mdt.gfx.gfx_np.get_pos(self.eng.gfx.root) + (0, 0, .5)
        self.eng.particle(self.eng.gfx.root, pos, (0, 0, 0), (1, .4, .1, 1), .8)
        self.mdt.destroy()

    def _eval_wall_coll(self, tgt_obj, obj):
        if tgt_obj.get_name() == 'Wall' and obj == self.mdt.phys.node:
            self.mdt.destroy()

    def destroy(self):
        self.eng.detach_obs(self.on_collision)
        EventColleague.destroy(self)


class RocketWeaponEvent(WeaponEvent):

    def on_collision(self, obj, tgt_obj):
        pnode = self.mdt.phys.node
        if tgt_obj.get_name() == self.wpn_name and tgt_obj == pnode:
            if obj.get_name() != 'Vehicle' or obj != self.mdt.logic.car.phys.pnode:
                int_lat = 10000
                int_rot = 20000
                obj.apply_central_force((choice([-int_lat, int_lat]), choice([-int_lat, int_lat]), 96000))
                obj.apply_torque((0, 0, choice([-int_rot, int_rot])))
                self.mdt.logic.notify('on_hit', obj)
                self._on_coll_success()
        self._eval_wall_coll(tgt_obj, obj)
