from panda3d.bullet import BulletRigidBodyNode, BulletSphereShape
from panda3d.core import Mat4, LVector3f
from yyagl.gameobject import Phys
from yyagl.engine.phys import PhysMgr


class MinePhys(Phys):

    cnt = 0

    def __init__(self, mdt, car):
        Phys.__init__(self, mdt)
        self.parent = car.gfx.nodepath
        self.car = car
        self.n_p = self.node = None
        MinePhys.cnt += 1
        self.minename = 'Mine' + str(MinePhys.cnt)

    def fire(self):
        self.node = BulletRigidBodyNode(self.minename)
        self.node.setMass(10000)
        self.node.addShape(BulletSphereShape(.5))
        self.n_p = self.parent.attachNewNode(self.node)
        self.n_p.setPos(0, 0, .5)
        self.n_p.wrt_reparent_to(render)
        self.n_p.set_pos(self.n_p.get_pos() - self.car.logic.car_vec * 2.5)        
        PhysMgr().attach_rigid_body(self.node)
        self.mdt.gfx.gfx_np.reparentTo(self.n_p)
        self.mdt.gfx.gfx_np.setPos(0, 0, 0)

    def destroy(self):
        if hasattr(self, 'node'):  # has not been fired
            PhysMgr().remove_rigid_body(self.node)
            self.n_p = self.n_p.remove_node()
        self.parent = None
        Phys.destroy(self)
