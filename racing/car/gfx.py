from os.path import exists
from panda3d.bullet import BulletRigidBodyNode
from yyagl.gameobject import Gfx
from yyagl.facade import Facade
from .skidmark import Skidmark


class CarGfxFacade(Facade):

    def __init__(self):
        self._fwd_mth('on_skidmarking', self.skidmark_mgr.on_skidmarking)
        self._fwd_mth('on_no_skidmarking', self.skidmark_mgr.on_no_skidmarking)


class CarGfx(Gfx, CarGfxFacade):

    def __init__(self, mdt, car_props, race_props):
        self.chassis_np = self.cnt = None
        self.cprops = car_props
        self.rprops = race_props
        self.wheels = {'fl': None, 'fr': None, 'rl': None, 'rr': None}
        self.nodepath = eng.attach_node(BulletRigidBodyNode('Vehicle'))
        self.skidmark_mgr = SkidmarkMgr(mdt)
        part_path = self.rprops.particle_path
        eng.particle(part_path, render, render, (0, 1.2, .75), .8)
        self.crash_cnt = 0
        self.last_crash_t = 0
        Gfx.__init__(self, mdt)
        CarGfxFacade.__init__(self)

    def async_bld(self):
        low_dam_fpath = self.rprops.damage_paths.low % self.cprops.name
        self.chassis_np_low = loader.loadModel(low_dam_fpath)
        self.chassis_np_hi = loader.loadModel(low_dam_fpath)
        fpath = self.rprops.model_name % self.cprops.name
        loader.loadModel(fpath, callback=self.load_wheels)

    def reparent(self):
        self.chassis_np.reparent_to(self.nodepath)
        chas = [self.chassis_np, self.chassis_np_low, self.chassis_np_hi]
        map(lambda cha: cha.set_depth_offset(-2), chas)
        map(lambda whl: whl.reparent_to(eng.gfx.root), self.wheels.values())
        # try RigidBodyCombiner for the wheels
        for cha in chas:
            cha.prepare_scene(base.win.get_gsg())
            cha.premunge_scene(base.win.get_gsg())
        taskMgr.add(self.preload_tsk, 'preload')
        self.cnt = 2

    def preload_tsk(self, tsk):
        if self.cnt:
            self.apply_damage()
            self.cnt -= 1
            return tsk.again
        else:
            self.apply_damage(True)

    def load_wheels(self, chassis_model):
        self.chassis_np = chassis_model
        load = eng.base.loader.loadModel
        fpath = self.rprops.wheel_gfx_names.front % self.cprops.name
        rpath = self.rprops.wheel_gfx_names.rear % self.cprops.name
        m_exists = lambda path: exists(path + '.egg') or exists(path + '.bam')
        b_path = self.rprops.wheel_gfx_names.both % self.cprops.name
        front_path = fpath if m_exists(fpath) else b_path
        rear_path = rpath if m_exists(rpath) else b_path
        self.wheels['fr'] = load(front_path)
        self.wheels['fl'] = load(front_path)
        self.wheels['rr'] = load(rear_path)
        self.wheels['rl'] = load(rear_path)
        Gfx._end_async(self)

    def crash_sfx(self):
        self.crash_cnt += 1
        if self.mdt.phys.prev_speed_ratio < .8 or \
                eng.curr_time - self.last_crash_t < 5.0 or self.crash_cnt < 2:
            return False
        # part_path = self.rprops.particle_path
        # node = self.mdt.gfx.nodepath
        # eng.particle(part_path, render, render,
        #              node.get_pos(render) + (0, 1.2, .75), .8)
        # particles are too slow
        self.apply_damage()
        return True

    def apply_damage(self, reset=False):
        curr_chassis = self.nodepath.get_children()[0]
        if reset:
            next_chassis = self.chassis_np
        elif self.chassis_np_low.get_name() in curr_chassis.get_name():
            next_chassis = self.chassis_np_hi
        elif self.chassis_np_hi.get_name() in curr_chassis.get_name():
            return
        else:
            next_chassis = self.chassis_np_low
        curr_chassis.remove_node()
        next_chassis.reparent_to(self.nodepath)
        if self.mdt.logic.weapon:
            self.mdt.logic.weapon.reparent(next_chassis)
        self.mdt.phys.apply_damage(reset)
        self.mdt.gui.apply_damage(reset)
        self.last_crash_t = eng.curr_time
        self.crash_cnt = 0

    def destroy(self):
        meshes = [self.nodepath, self.chassis_np] + self.wheels.values()
        map(lambda mesh: mesh.remove_node(), meshes)
        self.wheels = None
        self.skidmark_mgr.destroy()
        Gfx.destroy(self)


class CarPlayerGfx(CarGfx):

    def crash_sfx(self):
        if CarGfx.crash_sfx(self):
            self.mdt.audio.crash_high_speed_sfx.play()


class SkidmarkMgr(object):

    def __init__(self, car):
        self.l_skidmark = self.r_skidmark = None
        self.skidmarks = []
        self.car = car

    def on_skidmarking(self):
        fr_pos = self.car.gfx.wheels['fr'].get_pos(render)
        fl_pos = self.car.gfx.wheels['fl'].get_pos(render)
        heading = self.car.gfx.nodepath.get_h()
        if self.r_skidmark:
            self.r_skidmark.update(fr_pos, heading)
            self.l_skidmark.update(fl_pos, heading)
        else:
            radius = self.car.phys.vehicle.getWheels()[0].getWheelRadius()
            self.r_skidmark = Skidmark(fr_pos, radius, heading)
            self.l_skidmark = Skidmark(fl_pos, radius, heading)
            self.skidmarks += [self.l_skidmark, self.r_skidmark]
            # whl_radius = self.car.phys.vehicle.get_wheels()[2].get_wheel_radius()
            # whl_pos_l = self.car.phys.vehicle.get_wheels()[2].get_chassis_connection_point_cs() + (0, -whl_radius, -whl_radius + .05)
            # whl_pos_r = self.car.phys.vehicle.get_wheels()[3].get_chassis_connection_point_cs() + (0, -whl_radius, -whl_radius + .05)
            # eng.particle(
            #     'assets/particles/skidmark.ptf', self.car.gfx.nodepath,
            #     self.car.gfx.nodepath, whl_pos_l, 1.2, 'left skidmark')
            # eng.particle(
            #     'assets/particles/skidmark.ptf', self.car.gfx.nodepath,
            #     self.car.gfx.nodepath, whl_pos_r, 1.2, 'right skidmark')
            # particles are too slow

    def on_no_skidmarking(self):
        self.l_skidmark = self.r_skidmark = None

    def destroy(self):
        map(lambda skd: skd.destroy(), self.skidmarks)
        self.car = self.skidmarks = None
