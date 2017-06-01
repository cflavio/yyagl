from direct.interval.LerpInterval import LerpHprInterval
from yyagl.gameobject import Gfx


class RocketGfx(Gfx):

    def __init__(self, mdt, parent, path):
        self.gfx_np = None
        self.parent = parent
        self.path = path
        Gfx.__init__(self, mdt)

    def sync_bld(self):
        self.gfx_np = loader.loadModel(self.path)
        self.gfx_np.flattenLight()
        self.gfx_np.reparentTo(self.parent)
        self.gfx_np.set_h(180)
        self.gfx_np.set_scale(1.5)
        self.gfx_np.set_pos(0, 0, 1.5)
        self.ival = LerpHprInterval(self.gfx_np, 3, (180, 0, 360), (180, 0, 0))
        self.ival.loop()

    def destroy(self):
        self.gfx_np = self.gfx_np.remove_node()
        self.parent = self.ival = self.ival.finish()
        Gfx.destroy(self)
