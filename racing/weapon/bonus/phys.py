from panda3d.bullet import BulletBoxShape, BulletGhostNode
from yyagl.gameobject import Phys
from yyagl.engine.phys import PhysMgr


class BonusPhys(Phys):

    def __init__(self, mdt, pos):
        self.pos = pos
        self.ghost = None
        Phys.__init__(self, mdt)

    def sync_bld(self):
        self.ghost = BulletGhostNode('Bonus')
        self.ghost.addShape(BulletBoxShape((1, 1, 2.5)))
        ghost_np = eng.attach_node(self.ghost)
        ghost_np.setPos(self.pos)
        PhysMgr().attach_ghost(self.ghost)

    def destroy(self):
        self.ghost = PhysMgr().remove_ghost(self.ghost)
        Phys.destroy(self)
