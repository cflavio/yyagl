from panda3d.bullet import BulletRigidBodyNode, BulletSphereShape
from panda3d.core import Mat4
from yyagl.gameobject import Phys
from yyagl.engine.phys import PhysMgr


class RocketPhys(Phys):

    def __init__(self, mdt, parent):
        Phys.__init__(self, mdt)
        self.parent = parent
        self.n_p = self.node = None

    def fire(self):
        self.node = BulletRigidBodyNode('Box')
        self.node.setMass(10000)
        self.node.addShape(BulletSphereShape(.5))
        self.n_p = self.parent.attachNewNode(self.node)
        self.n_p.setPos(0, 0, 1.5)
        PhysMgr().attach_rigid_body(self.node)
        self.mdt.gfx.gfx_np.reparentTo(self.n_p)
        self.mdt.gfx.gfx_np.setPos(0, 0, 0)
        rot_mat = Mat4()
        rot_mat.setRotateMat(self.parent.get_h(), (0, 0, 1))
        self.node.setLinearVelocity(rot_mat.xformVec((0, 30, 0)))
        # continue to apply after firing

    def destroy(self):
        if hasattr(self, 'node'):  # has not been fired
            PhysMgr().remove_rigid_body(self.node)
            self.n_p = self.n_p.remove_node()
        self.parent = None
        Phys.destroy(self)
