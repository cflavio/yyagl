from panda3d.core import Vec3
from direct.interval.LerpInterval import LerpPosInterval, LerpHprInterval
from direct.interval.IntervalGlobal import LerpFunc
from direct.actor.Actor import Actor
from yyagl.gameobject import Gfx


class WeaponGfx(Gfx):

    def __init__(self, mdt, parent, fpath):
        self.gfx_np = None
        self.parent = parent
        self.fpath = fpath
        Gfx.__init__(self, mdt)

    def update_props(self, pos, fwd):
        pass

    def sync_bld(self):
        self.gfx_np = self.eng.load_model(self.fpath, anim={'anim': self.fpath + '-Anim'})
        self.gfx_np.loop('anim')
        #self.gfx_np.flatten_light()
        self.gfx_np.reparent_to(self.parent)
        self.gfx_np.set_h(self.mdt.deg)
        self.gfx_np.set_scale(1.5)
        self.gfx_np.set_pos((0, 0, 1.5))

    def reparent(self, parent):
        self.gfx_np.reparent_to(parent)

    def destroy(self):
        self.gfx_np.cleanup()
        self.parent = self.gfx_np = self.gfx_np.remove_node()
        Gfx.destroy(self)


class WeaponGfxNetwork(WeaponGfx):

    def __init__(self, mdt, car, cars):
        WeaponGfx.__init__(self, mdt, car, cars)
        self.ipos = None
        self.ifwd = None

    def update_props(self, pos, fwd):
        if pos == (0, 0, 0) and fwd == (0, 0, 0): return
        wpn_np = self.gfx_np.node
        self.gfx_np.node.reparent_to(render)
        self.ipos = LerpPosInterval(wpn_np, self.eng.client.rate, pos)
        self.ipos.start()
        fwd_start = render.get_relative_vector(wpn_np, Vec3(0, 1, 0))
        self.ifwd = LerpFunc(self._rotate_wpn,
                             fromData=0,
                             toData=1,
                             duration=self.eng.client.rate,
                             extraArgs=[wpn_np, fwd_start, fwd])
        self.ifwd.start()

    @staticmethod
    def _rotate_wpn(t, node, start_vec, end_vec):
        interp_vec = Vec3(
            start_vec[0] * (1 - t) + end_vec[0] * t,
            start_vec[1] * (1 - t) + end_vec[1] * t,
            start_vec[2] * (1 - t) + end_vec[2] * t)
        node.look_at(node.get_pos() + interp_vec)

    def destroy(self):
        if self.ipos: self.ipos.finish()
        if self.ifwd: self.ifwd.finish()
        self.ipos = self.ifwd = None
        WeaponGfx.destroy(self)
