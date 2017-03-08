from yyagl.gameobject import Phys
from panda3d.bullet import BulletBoxShape, BulletGhostNode


class BonusPhys(Phys):

    def __init__(self, mdt, pos):
        self.pos = pos
        Phys.__init__(self, mdt)

    def sync_build(self):
        self.ghost = BulletGhostNode('Bonus')
        self.ghost.addShape(BulletBoxShape((1, 1, 2.5)))
        ghostNP = render.attachNewNode(self.ghost)  # facade
        ghostNP.setPos(self.pos)
        eng.phys.world_phys.attachGhost(self.ghost)  # facade

    def destroy(self):
        self.ghost = eng.phys.world_phys.removeGhost(self.ghost)  # facade
        Phys.destroy(self)
