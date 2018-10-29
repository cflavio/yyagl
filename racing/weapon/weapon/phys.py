from panda3d.bullet import BulletRigidBodyNode
from panda3d.core import Mat4, BitMask32
from yyagl.gameobject import PhysColleague
from yyagl.racing.bitmasks import BitMasks
from yyagl.engine.vec import Vec


class WeaponPhys(PhysColleague):

    def __init__(self, mediator, car, cars):
        PhysColleague.__init__(self, mediator)
        self.parent, self.car, self.cars = car.gfx.nodepath, car, cars
        self.n_p = self.node = None

    def fire(self):
        self.node = BulletRigidBodyNode(self.coll_name)
        self.node.set_mass(50)
        self.node.add_shape(self.coll_mesh_cls(.5))
        self.n_p = self.parent.attach_node(self.node)
        self.n_p.set_pos(Vec(0, 0, self.joint_z))
        self.n_p.wrt_reparent_to(self.eng.gfx.root)
        launch_dist = self.car.logic.car_vec * self.launch_dist
        pos = self.n_p.get_pos()
        pos = Vec(pos.x, pos.y, pos.z)
        self.n_p.set_pos(pos + launch_dist)
        self.eng.phys_mgr.attach_rigid_body(self.node)
        self.mediator.gfx.gfx_np.reparent_to(self.n_p)
        self.mediator.gfx.gfx_np.set_pos(Vec(0, 0, self.gfx_dz))

    def destroy(self):
        if self.node:  # has not been fired
            self.eng.phys_mgr.remove_rigid_body(self.node)
            self.n_p = self.n_p.remove_node()
        self.parent = None
        PhysColleague.destroy(self)


class RocketWeaponPhys(WeaponPhys):

    def __init__(self, mediator, car, cars):
        WeaponPhys.__init__(self, mediator, car, cars)
        self.update_tsk = self.rot_mat = None
        self.coll_name = self.rocket_coll_name

    def fire(self):
        WeaponPhys.fire(self)
        b_m = BitMask32.bit(BitMasks.general)
        cars_idx = range(len(self.car.logic.cprops.race_props.season_props.car_names))
        cars_idx.remove(
            self.car.logic.cprops.race_props.season_props.car_names.index(self.car.name))
        for bitn in cars_idx:
            b_m = b_m | BitMask32.bit(BitMasks.car(bitn))
        self.n_p.set_collide_mask(b_m)
        self.eng.phys_mgr.add_collision_obj(self.node)
        self.node.set_python_tag('car', self.mediator.logic.car)
        self.rot_mat = Mat4()
        rot_deg = self.parent.h + self.rot_deg
        self.rot_mat.set_rotate_mat(rot_deg, (0, 0, 1))
        self.update_tsk = taskMgr.add(self.update_weapon, 'update_weapon')

    def __new_val(self, val, tgt, incr):
        if abs(val - tgt) <= incr:
            return tgt
        return val + incr if tgt > val else val - incr

    def update_weapon(self, tsk):
        if not self.n_p: return
        # hotfix: it may happen that
        # node_pos = self.n_p.get_pos()  <- self.n_p is None
        # we should give priorities to tasks, e.g. run on_frame after these ones
        # Traceback (most recent call last):
        #   File "C:\buildslave\rtdist-windows-i386\build\built\direct\p3d\AppRunner.py", line 596, in run
        #   File "C:\buildslave\rtdist-windows-i386\build\built\direct\task\Task.py", line 513, in run
        #   File "C:\buildslave\rtdist-windows-i386\build\built\direct\task\Task.py", line 470, in step
        #   File "yyagl/racing/weapon/weapon/phys.py", line 55, in update_weapon
        # AttributeError: 'NoneType' object has no attribute 'get_pos'
        self.node.set_linear_velocity(self.rot_mat.xform_vec((0, 60, 0)))
        node_pos = self.n_p.get_pos()
        height = self.car.phys.gnd_height(node_pos) + .8
        new_height = self.__new_val(node_pos[2], height, globalClock.getDt() * 4.0)
        self.n_p.set_pos(Vec(node_pos[0], node_pos[1], new_height))
        return tsk.again

    def destroy(self):
        if self.node: self.eng.phys_mgr.remove_collision_obj(self.node)
        if self.update_tsk: self.update_tsk = taskMgr.remove(self.update_tsk)
        WeaponPhys.destroy(self)
