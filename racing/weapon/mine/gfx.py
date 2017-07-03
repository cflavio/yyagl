from direct.actor.Actor import Actor
from yyagl.gameobject import Gfx


class MineGfx(Gfx):

    def __init__(self, mdt, parent, path):
        self.gfx_np = None
        self.parent = parent
        self.path = path
        self.ival = None
        Gfx.__init__(self, mdt)

    def sync_bld(self):
        self.gfx_np = Actor(self.path, {'anim': self.path + '-Anim'})
        self.gfx_np.loop('anim')
        self.gfx_np.flattenLight()
        self.gfx_np.reparentTo(self.parent)
        self.gfx_np.set_h(180)
        self.gfx_np.set_scale(1.5)
        self.gfx_np.set_pos(0, 0, 1.5)

    def destroy(self):
        self.parent = self.gfx_np = self.gfx_np.remove_node()
        Gfx.destroy(self)
