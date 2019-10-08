from panda3d.core import Vec3, NodePath
from direct.interval.LerpInterval import LerpPosInterval, LerpHprInterval
from direct.interval.IntervalGlobal import LerpFunc
from direct.actor.Actor import Actor
from yyagl.gameobject import GfxColleague
from yyagl.engine.vec import Vec


class WeaponGfx(GfxColleague):

    def __init__(self, mediator, parent, fpath):
        self.gfx_np = None
        self.parent = parent
        self.fpath = fpath
        GfxColleague.__init__(self, mediator)
        self.gfx_np = self.eng.load_model(self.fpath, anim={'anim': self.fpath + '-Anim'})
        self.gfx_np.loop('anim')
        #self.gfx_np.flatten_light()
        self.gfx_np.reparent_to(self.parent)
        self.gfx_np.set_h(self.mediator.deg)
        self.gfx_np.set_scale(1.5)
        self.gfx_np.set_pos(Vec(0, 0, 1.5))
        self.gfx_np.set_depth_offset(1)

    def update_props(self, pos, fwd):
        pass

    def update_fired_props(self, pos, fwd):
        pass

    def reparent(self, parent):
        self.gfx_np.reparent_to(parent)

    def destroy(self):
        self.gfx_np.cleanup()
        self.parent = self.gfx_np = self.gfx_np.remove_node()
        GfxColleague.destroy(self)


class WeaponGfxNetwork(WeaponGfx):

    def __init__(self, mediator, car, cars):
        WeaponGfx.__init__(self, mediator, car, cars)
        self.ipos = None
        self.ifwd = None

    def update_props(self, pos, fwd):
        if pos == (0, 0, 0) and fwd == (0, 0, 0): return
        wpn_np = self.gfx_np.node
        old_pos = wpn_np.get_pos(render)
        self.gfx_np.node.reparent_to(render)
        wpn_np.set_pos(old_pos)
        self.ipos = LerpPosInterval(wpn_np, self.eng.client.rate, pos)
        self.ipos.start()
        fwd_start = render.get_relative_vector(wpn_np, Vec3(0, 1, 0))
        if self.ifwd: self.ifwd.finish()
        self.ifwd = LerpFunc(self._rotate_wpn,
                             fromData=0,
                             toData=1,
                             duration=self.eng.client.rate,
                             extraArgs=[wpn_np, fwd_start, fwd])
        self.ifwd.start()

    def update_fired_props(self, pos, fwd):
        if pos == (0, 0, 0) and fwd == (0, 0, 0): return
        wpn_np = self.gfx_np.node
        old_pos = wpn_np.get_pos(render)
        self.gfx_np.node.reparent_to(render)
        wpn_np.set_pos(old_pos)
        self.ipos = LerpPosInterval(wpn_np, self.eng.client.rate, pos)
        self.ipos.start()
        fwd_start = render.get_relative_vector(wpn_np, Vec3(0, 1, 0))
        if self.ifwd: self.ifwd.finish()
        self.ifwd = LerpFunc(self._rotate_wpn,
                             fromData=0,
                             toData=1,
                             duration=self.eng.client.rate,
                             extraArgs=[wpn_np, fwd_start, fwd])
        self.ifwd.start()

    @staticmethod
    def _rotate_wpn(t, node, start_vec, end_vec):
        interp_vec = Vec3(
            float(start_vec[0]) * (1 - t) + float(end_vec[0]) * t,
            float(start_vec[1]) * (1 - t) + float(end_vec[1]) * t,
            float(start_vec[2]) * (1 - t) + float(end_vec[2]) * t)
        node.look_at(node.get_pos() + interp_vec)

    def destroy(self):
        if self.ipos: self.ipos.finish()
        if self.ifwd: self.ifwd.finish()
        self.ipos = self.ifwd = None
        WeaponGfx.destroy(self)
