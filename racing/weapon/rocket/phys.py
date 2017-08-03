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
        self.update_tsk = self.rocket_np = self.phys_node = self.rot_mat = None

    def fire(self):
        self.phys_node = BulletRigidBodyNode('Rocket')
        self.phys_node.set_mass(10000)
        self.phys_node.add_shape(BulletSphereShape(.5))
        self.rocket_np = self.parent.attach_new_node(self.phys_node)
        self.rocket_np.set_pos(0, 0, .8)
        self.rocket_np.wrt_reparent_to(render)
        rocket_pos = self.rocket_np.get_pos() + self.car.logic.car_vec * 3.5
        self.rocket_np.set_pos(rocket_pos)
        b_m = BitMask32.bit(0)
        for bitn in range(len(self.cars)):
            b_m = b_m | BitMask32.bit(2 + bitn)
        self.rocket_np.set_collide_mask(b_m)
        PhysMgr().add_collision_obj(self.phys_node)
        PhysMgr().attach_rigid_body(self.phys_node)
        self.mdt.gfx.gfx_np.reparentTo(self.rocket_np)
        self.mdt.gfx.gfx_np.setPos(0, 0, 0)
        self.rot_mat = Mat4()
        self.rot_mat.set_rotate_mat(self.parent.get_h(), (0, 0, 1))
        self.update_tsk = taskMgr.add(self.update_weapon, 'update_weapon')

    def update_weapon(self, tsk):
        self.phys_node.set_linear_velocity(self.rot_mat.xform_vec((0, 60, 0)))
        node_pos = self.rocket_np.get_pos()
        height = self.car.phys.gnd_height(node_pos)
        self.rocket_np.set_pos(node_pos[0], node_pos[1], height + .8)
        return tsk.again

    def destroy(self):
        if self.phys_node:  # has not been fired
            PhysMgr().remove_rigid_body(self.phys_node)
            PhysMgr().remove_collision_obj(self.phys_node)
            self.rocket_np = self.rocket_np.remove_node()
        self.parent = None
        if self.update_tsk:
            self.update_tsk = taskMgr.remove(self.update_tsk)
        Phys.destroy(self)
