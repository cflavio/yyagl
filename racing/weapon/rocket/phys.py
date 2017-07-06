from panda3d.bullet import BulletRigidBodyNode, BulletSphereShape
from panda3d.core import Mat4, BitMask32
from yyagl.gameobject import Phys
from yyagl.engine.phys import PhysMgr


class RocketPhys(Phys):

    def __init__(self, mdt, car, cars):
        Phys.__init__(self, mdt)
        self.parent = car.gfx.nodepath
        self.car = car
        self.cars = cars
        self.update_tsk = self.n_p = self.node = None

    def fire(self):
        self.node = BulletRigidBodyNode('Rocket')
        self.node.setMass(10000)
        self.node.addShape(BulletSphereShape(.5))
        self.n_p = self.parent.attachNewNode(self.node)
        self.n_p.setPos(0, 0, .8)
        self.n_p.wrt_reparent_to(render)
        self.n_p.set_pos(self.n_p.get_pos() + self.car.logic.car_vec * 3.5)
        b_m = BitMask32.bit(0)
        for bitn in range(len(self.cars)):
            b_m = b_m | BitMask32.bit(2 + bitn)
        self.n_p.setCollideMask(b_m)
        PhysMgr().add_collision_obj(self.node)
        PhysMgr().attach_rigid_body(self.node)
        self.mdt.gfx.gfx_np.reparentTo(self.n_p)
        self.mdt.gfx.gfx_np.setPos(0, 0, 0)
        self.rot_mat = Mat4()
        self.rot_mat.setRotateMat(self.parent.get_h(), (0, 0, 1))
        self.update_tsk = taskMgr.add(self.update_weapon, 'update_weapon')

    def update_weapon(self, tsk):
        self.node.setLinearVelocity(self.rot_mat.xformVec((0, 60, 0)))
        node_pos = self.n_p.get_pos()
        height = self.car.phys.gnd_height(node_pos)
        self.n_p.set_pos(node_pos[0], node_pos[1], height + .8)
        return tsk.again

    def destroy(self):
        if hasattr(self, 'node'):  # has not been fired
            PhysMgr().remove_rigid_body(self.node)
            PhysMgr().remove_collision_obj(self.node)
            self.n_p = self.n_p.remove_node()
        self.parent = None
        self.update_tsk = taskMgr.remove(self.update_tsk)
        Phys.destroy(self)
