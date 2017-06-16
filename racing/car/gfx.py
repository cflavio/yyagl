from os.path import exists
from panda3d.bullet import BulletRigidBodyNode
from panda3d.core import NodePath
from yyagl.gameobject import Gfx
from .skidmark import Skidmark


class CarGfxFacade:

    def on_skidmarking(self):
        self.skidmark_mgr.on_skidmarking()

    def on_no_skidmarking(self):
        self.skidmark_mgr.on_no_skidmarking()


class CarGfx(Gfx, CarGfxFacade):

    def __init__(self, mdt, cargfx_props):
        self.chassis_np = None
        self.props = cargfx_props
        self.wheels = {'fl': None, 'fr': None, 'rl': None, 'rr': None}
        vehicle_node = BulletRigidBodyNode('Vehicle')
        self.nodepath = eng.attach_node(vehicle_node)
        self.skidmark_mgr = SkidmarkMgr(mdt)
        part_path = self.props.particle_path
        eng.particle(part_path, render, render, (0, 1.2, .75), .8)
        Gfx.__init__(self, mdt)

    def async_bld(self):
        fpath = self.props.model_name % self.mdt.name
        path = self.props.damage_paths[0] % self.mdt.name
        self.chassis_np_low = loader.loadModel(path)
        path = self.props.damage_paths[1] % self.mdt.name
        self.chassis_np_hi = loader.loadModel(path)
        loader.loadModel(fpath, callback=self.load_wheels)

    def reparent(self):
        self.chassis_np.reparentTo(self.nodepath)
        cha = [self.chassis_np, self.chassis_np_low, self.chassis_np_hi]
        map(lambda cha: cha.setDepthOffset(-2), cha)
        map(lambda whl: whl.reparentTo(eng.gfx.root), self.wheels.values())
        # try RigidBodyCombiner for the wheels
        for model in [self.chassis_np, self.chassis_np_low, self.chassis_np_hi]:
            model.prepare_scene(base.win.getGsg())
            model.premunge_scene(base.win.getGsg())
        taskMgr.add(self.preload_tsk, 'preload')
        self.cnt = 2

    def preload_tsk(self, task):
        if self.cnt:
            self.apply_damage()
            self.cnt -= 1
            return task.again
        else:
            self.apply_damage(True)

    def load_wheels(self, chassis_model):
        self.chassis_np = chassis_model
        load = eng.base.loader.loadModel
        fpath = self.props.wheel_gfx_names[0] % self.mdt.name
        rpath = self.props.wheel_gfx_names[1] % self.mdt.name
        m_exists = lambda path: exists(path + '.egg') or exists(path + '.bam')
        a_path = self.props.wheel_gfx_names[2] % self.mdt.name
        front_path = fpath if m_exists(fpath) else a_path
        rear_path = rpath if m_exists(rpath) else a_path
        self.wheels['fr'] = load(front_path)
        self.wheels['fl'] = load(front_path)
        self.wheels['rr'] = load(rear_path)
        self.wheels['rl'] = load(rear_path)
        Gfx._end_async(self)

    def crash_sfx(self):
        if self.mdt.phys.prev_speed_ratio < .64:
            return
        self.mdt.audio.crash_high_speed_sfx.play()
        part_path = self.props.particle_path
        node = self.mdt.gfx.nodepath
        eng.particle(part_path, node, eng.base.render, (0, 1.2, .75), .8)
        self.apply_damage()

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
        self.mdt.phys.apply_damage(reset)
        self.mdt.gui.apply_damage(reset)

    def destroy(self):
        meshes = [self.nodepath, self.chassis_np] + self.wheels.values()
        map(lambda mesh: mesh.removeNode(), meshes)
        self.wheels = None
        self.skidmark_mgr.destroy()
        Gfx.destroy(self)


class SkidmarkMgr:

    def __init__(self, car):
        self.l_skidmark = self.r_skidmark = None
        self.skidmarks = []
        self.car = car

    def on_skidmarking(self):
        frpos = self.car.gfx.wheels['fr'].get_pos(render)
        flpos = self.car.gfx.wheels['fl'].get_pos(render)
        heading = self.car.gfx.nodepath.get_h()
        if self.r_skidmark:
            self.r_skidmark.update(frpos, heading)
            self.l_skidmark.update(flpos, heading)
        else:
            radius = self.car.phys.vehicle.getWheels()[0].getWheelRadius()
            self.r_skidmark = Skidmark(frpos, radius, heading)
            self.l_skidmark = Skidmark(flpos, radius, heading)
            self.skidmarks += [self.l_skidmark, self.r_skidmark]

    def on_no_skidmarking(self):
        self.l_skidmark = self.r_skidmark = None

    def destroy(self):
        map(lambda skd: skd.destroy(), self.skidmarks)
        self.car = self.skidmarks = None
