from os.path import exists
from yyagl.gameobject import Gfx
from panda3d.bullet import BulletRigidBodyNode
from .skidmark import Skidmark


class CarGfx(Gfx):

    def __init__(self, mdt, path):
        self.chassis_np = None
        self.wheels = {'fl': None, 'fr': None, 'rl': None, 'rr': None}
        vehicle_node = BulletRigidBodyNode('Vehicle')
        self.nodepath = eng.gfx.world_np.attachNewNode(vehicle_node)
        Gfx.__init__(self, mdt)
        self.l_skidmark = self.r_skidmark = None
        self.skidmarks = []

    def on_skidmarking(self):
        if self.r_skidmark:
            self.r_skidmark.update()
            self.l_skidmark.update()
        else:
            self.r_skidmark = Skidmark(self.mdt, 'fr')
            self.l_skidmark = Skidmark(self.mdt, 'fl')
            self.skidmarks += [self.l_skidmark, self.r_skidmark]

    def on_no_skidmarking(self):
        self.r_skidmark = None
        self.l_skidmark = None

    def async_build(self):
        try:
            path = self.mdt.path + '/cardamage1'
            self.chassis_np_low = loader.loadModel(path)
        except IOError:
            self.chassis_np_low = loader.loadModel(self.mdt.path + '/car')
        try:
            path = self.mdt.path + '/cardamage2'
            self.chassis_np_hi = loader.loadModel(path)
        except IOError:
            self.chassis_np_hi = loader.loadModel(self.mdt.path + '/car')
        loader.loadModel(self.mdt.path + '/car', callback=self.load_wheels)

    def reparent(self):
        self.chassis_np.reparentTo(self.nodepath)
        cha = [self.chassis_np, self.chassis_np_low, self.chassis_np_hi]
        map(lambda cha: cha.setDepthOffset(-2), cha)

        map(lambda whl: whl.reparentTo(eng.gfx.world_np), self.wheels.values())

    def load_wheels(self, chassis_model):
        self.chassis_np = chassis_model
        load = eng.base.loader.loadModel
        fpath = 'assets/models/' + self.mdt.path + '/wheelfront'
        rpath = 'assets/models/' + self.mdt.path + '/wheelrear'
        m_exists = lambda path: exists(path + '.egg') or exists(path + '.bam')
        front_path = fpath if m_exists(fpath) else self.mdt.path + '/wheel'
        rear_path = rpath if m_exists(rpath) else self.mdt.path + '/wheel'
        self.wheels['fr'] = load(front_path)
        self.wheels['fl'] = load(front_path)
        self.wheels['rr'] = load(rear_path)
        self.wheels['rl'] = load(rear_path)
        Gfx._end_async(self)

    def crash_sfx(self):
        if self.mdt.phys.speed_ratio < .5:
            return
        self.apply_damage()
        self.mdt.audio.crash_high_speed_sfx.play()
        part_path = 'assets/particles/sparks.ptf'
        node = self.mdt.gfx.nodepath
        eng.gfx.particle(part_path, node, eng.base.render, (0, 1.2, .75), .8)

    def apply_damage(self, reset=False):
        curr_chassis = self.nodepath.get_children()[0]
        if reset:
            next_chassis = self.chassis_np
        elif 'cardamage1' in curr_chassis.get_name():
            next_chassis = self.chassis_np_hi
        elif 'cardamage2' in curr_chassis.get_name():
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
        map(lambda skd: skd.destroy(), self.skidmarks)
        Gfx.destroy(self)
