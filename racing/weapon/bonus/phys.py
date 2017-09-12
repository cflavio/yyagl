from panda3d.bullet import BulletBoxShape, BulletGhostNode
from yyagl.gameobject import Phys


class BonusPhys(Phys):

    def __init__(self, mdt, pos):
        self.pos = pos
        self.ghost = None
        Phys.__init__(self, mdt)

    def sync_bld(self):
        self.ghost = BulletGhostNode('Bonus')
        self.ghost.add_shape(BulletBoxShape((1, 1, 2.5)))
        ghost_np = self.eng.attach_node(self.ghost)
        ghost_np.set_pos(self.pos)
        self.eng.phys_mgr.attach_ghost(self.ghost)

    def destroy(self):
        self.ghost = self.eng.phys_mgr.remove_ghost(self.ghost)
        Phys.destroy(self)
