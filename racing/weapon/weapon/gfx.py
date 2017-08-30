from direct.actor.Actor import Actor
from yyagl.gameobject import Gfx


class WeaponGfx(Gfx):

    def __init__(self, mdt, parent, fpath, deg=0):
        self.gfx_np = None
        self.parent = parent
        self.fpath = fpath
        self.deg = deg
        Gfx.__init__(self, mdt)

    def sync_bld(self):
        self.gfx_np = Actor(self.fpath, {'anim': self.fpath + '-Anim'})
        self.gfx_np.loop('anim')
        self.gfx_np.flatten_light()
        self.gfx_np.reparent_to(self.parent)
        self.gfx_np.set_h(self.deg)
        self.gfx_np.set_scale(1.5)
        self.gfx_np.set_pos(0, 0, 1.5)

    def reparent(self, parent):
        self.gfx_np.reparent_to(parent)

    def destroy(self):
        self.gfx_np.cleanup()
        self.parent = self.gfx_np = self.gfx_np.remove_node()
        Gfx.destroy(self)
