from panda3d.bullet import BulletRigidBodyNode, BulletSphereShape
from panda3d.core import Mat4, BitMask32
from yyagl.gameobject import Phys
from yyagl.engine.phys import PhysMgr


class WeaponPhys(Phys):

    def __init__(self, mdt, car, cars):
        Phys.__init__(self, mdt)
        self.parent, self.car, self.cars = car.gfx.nodepath, car, cars
        self.n_p = self.node = None

    def fire(self):
        self.node = BulletRigidBodyNode(self.coll_name)
        self.node.set_mass(10000)
        self.node.add_shape(self.coll_mesh_cls(.5))
        self.n_p = self.parent.attach_new_node(self.node)
        self.n_p.set_pos(0, 0, self.joint_z)
        self.n_p.wrt_reparent_to(render)
        launch_dist = self.car.logic.car_vec * self.launch_dist
        self.n_p.set_pos(self.n_p.get_pos() + launch_dist)
        self.eng.phys_mgr.attach_rigid_body(self.node)
        self.mdt.gfx.gfx_np.reparentTo(self.n_p)
        self.mdt.gfx.gfx_np.setPos(0, 0, 0)

    def destroy(self):
        if self.node:  # has not been fired
            self.eng.phys_mgr.remove_rigid_body(self.node)
            self.n_p = self.n_p.remove_node()
        self.parent = None
        Phys.destroy(self)


class RocketWeaponPhys(WeaponPhys):

    def __init__(self, mdt, car, cars):
        WeaponPhys.__init__(self, mdt, car, cars)
        self.update_tsk = self.rot_mat = None
        self.coll_name = self.rocket_coll_name

    def fire(self):
        WeaponPhys.fire(self)
        b_m = BitMask32.bit(0)
        for bitn in range(len(self.cars)):
            b_m = b_m | BitMask32.bit(2 + bitn)
        self.n_p.set_collide_mask(b_m)
        self.eng.phys_mgr.add_collision_obj(self.node)
        self.rot_mat = Mat4()
        self.rot_mat.set_rotate_mat(self.parent.get_h() + self.rot_deg, (0, 0, 1))
        self.update_tsk = taskMgr.add(self.update_weapon, 'update_weapon')

    def update_weapon(self, tsk):
        self.node.set_linear_velocity(self.rot_mat.xform_vec((0, 60, 0)))
        node_pos = self.n_p.get_pos()
        height = self.car.phys.gnd_height(node_pos)
        self.n_p.set_pos(node_pos[0], node_pos[1], height + .8)
        return tsk.again

    def destroy(self):
        if self.node: self.eng.phys_mgr.remove_collision_obj(self.node)
        if self.update_tsk: self.update_tsk = taskMgr.remove(self.update_tsk)
        WeaponPhys.destroy(self)
