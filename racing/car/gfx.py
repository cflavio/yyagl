from os.path import exists
from panda3d.bullet import BulletRigidBodyNode
from yyagl.gameobject import Gfx
from .skidmark import Skidmark


class CarGfxFacade:

    def on_skidmarking(self):
        self.skidmark_mgr.on_skidmarking()

    def on_no_skidmarking(self):
        self.skidmark_mgr.on_no_skidmarking()


class CarGfx(Gfx, CarGfxFacade):

    def __init__(self, mdt, path, base_path, model_name, damage_paths,
                 wheel_gfx_names, particle_path):
        self.chassis_np = None
        self.base_path = base_path
        self.model_name = model_name
        self.damage_paths = damage_paths
        self.wheel_gfx_names = wheel_gfx_names
        self.particle_path = particle_path
        self.wheels = {'fl': None, 'fr': None, 'rl': None, 'rr': None}
        vehicle_node = BulletRigidBodyNode('Vehicle')
        self.nodepath = eng.gfx.world_np.attachNewNode(vehicle_node)  # facade
        self.skidmark_mgr = SkidmarkMgr(mdt)
        Gfx.__init__(self, mdt)

    def async_build(self):
        base_path = self.base_path + '/' + self.mdt.name
        fpath = base_path + '/' + self.model_name
        try:
            path = base_path + '/' + self.damage_paths[0]
            self.chassis_np_low = loader.loadModel(path)
        except IOError:
            self.chassis_np_low = loader.loadModel(fpath)
        try:
            path = base_path + '/' + self.damage_paths[1]
            self.chassis_np_hi = loader.loadModel(path)
        except IOError:
            self.chassis_np_hi = loader.loadModel(fpath)
        loader.loadModel(fpath, callback=self.load_wheels)

    def reparent(self):
        self.chassis_np.reparentTo(self.nodepath)
        cha = [self.chassis_np, self.chassis_np_low, self.chassis_np_hi]
        map(lambda cha: cha.setDepthOffset(-2), cha)
        map(lambda whl: whl.reparentTo(eng.gfx.world_np), self.wheels.values())
        # try RigidBodyCombiner

    def load_wheels(self, chassis_model):
        self.chassis_np = chassis_model
        load = eng.base.loader.loadModel
        names = [self.base_path, self.mdt.name, self.wheel_gfx_names[0]]
        fpath = '/'.join(names)
        names = [self.base_path, self.mdt.name, self.wheel_gfx_names[1]]
        rpath = '/'.join(names)
        m_exists = lambda path: exists(path + '.egg') or exists(path + '.bam')
        names = [self.base_path, self.mdt.name, self.wheel_gfx_names[2]]
        a_path = '/'.join(names)
        front_path = fpath if m_exists(fpath) else a_path
        rear_path = rpath if m_exists(rpath) else a_path
        self.wheels['fr'] = load(front_path)
        self.wheels['fl'] = load(front_path)
        self.wheels['rr'] = load(rear_path)
        self.wheels['rl'] = load(rear_path)
        Gfx._end_async(self)

    def crash_sfx(self):
        if self.mdt.phys.speed_ratio < .5:
            return
        self.mdt.audio.crash_high_speed_sfx.play()
        part_path = self.particle_path
        node = self.mdt.gfx.nodepath
        eng.gfx.particle(part_path, node, eng.base.render, (0, 1.2, .75), .8)
        self.apply_damage()

    def apply_damage(self, reset=False):
        curr_chassis = self.nodepath.get_children()[0]
        if reset:
            next_chassis = self.chassis_np
        elif self.damage_paths[0] in curr_chassis.get_name():
            next_chassis = self.chassis_np_hi
        elif self.damage_paths[1] in curr_chassis.get_name():
            return
        else:
            next_chassis = self.chassis_np_low
        curr_chassis.remove_node()
        next_chassis.reparent_to(self.nodepath)
        self.mdt.phys.apply_damage()
        self.mdt.gui.apply_damage()

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
        if self.r_skidmark:
            self.r_skidmark.update()
            self.l_skidmark.update()
        else:
            self.r_skidmark = Skidmark(self.car, 'fr')
            self.l_skidmark = Skidmark(self.car, 'fl')
            self.skidmarks += [self.l_skidmark, self.r_skidmark]

    def on_no_skidmarking(self):
        self.r_skidmark = None
        self.l_skidmark = None

    def destroy(self):
        map(lambda skd: skd.destroy(), self.skidmarks)
        self.car = self.skidmarks = None
