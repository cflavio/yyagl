from math import pi
from yaml import load as yaml_load
from os.path import exists
from panda3d.bullet import BulletRigidBodyNode
from yyagl.gameobject import GfxColleague, GameObject
from yyagl.facade import Facade
from .skidmark import Skidmark
from .decorator import Decorator
from yyagl.racing.weapon.rocket.rocket import Rocket
from yyagl.racing.weapon.rear_rocket.rear_rocket import RearRocket
from yyagl.racing.weapon.turbo.turbo import Turbo
from yyagl.racing.weapon.rotate_all.rotate_all import RotateAll
from yyagl.racing.weapon.mine.mine import Mine


class CarGfxFacade(Facade):

    def __init__(self):
        self._fwd_mth('on_skidmarking',
                      lambda obj: obj.skidmark_mgr.on_skidmarking)
        self._fwd_mth('on_no_skidmarking',
                      lambda obj: obj.skidmark_mgr.on_no_skidmarking)


class CarGfx(GfxColleague, CarGfxFacade):

    def __init__(self, mediator, car_props):
        self.chassis_np = self.cnt = self.chassis_np_low = \
            self.chassis_np_hi = None
        self.cprops = car_props
        self.wheels = {'fl': None, 'fr': None, 'rl': None, 'rr': None}
        self.nodepath = self.eng.attach_node(BulletRigidBodyNode('Vehicle'))
        self.skidmark_mgr = SkidmarkMgr(mediator)
        self.crash_cnt = 0
        self.last_crash_t = 0
        self.decorators = []
        self.dec_tsk = []
        GfxColleague.__init__(self, mediator)
        CarGfxFacade.__init__(self)
        self.load()

    def set_decorator(self, dec_code):
        deccode2info = {
            'pitstop': ('PitStop/PitStopAnim', 5.0),
            'rotate_all': ('RotateAllHit/RotateAllHitAnim', 3.0)}
        info = deccode2info[dec_code]
        fpath = 'assets/models/misc/' + info[0]
        self.decorators += [Decorator(fpath, self.nodepath)]
        args = info[1], self.unset_decorator, [self.decorators[-1]]
        self.dec_tsk += [self.eng.do_later(*args)]

    def unset_decorator(self, dec):
        self.decorators.remove(dec)
        dec.destroy()

    def load(self):
        gprops = self.cprops.race_props.season_props.gameprops
        low_dam_fpath = gprops.damage_paths.low % self.cprops.name
        hi_dam_fpath = gprops.damage_paths.hi % self.cprops.name
        self.chassis_np_low = self.eng.load_model(low_dam_fpath)
        self.chassis_np_hi = self.eng.load_model(hi_dam_fpath)
        fpath = gprops.model_name % self.cprops.name
        chassis = self.eng.load_model(fpath)
        ppath = self.cprops.race_props.season_props.gameprops.phys_path
        fpath = ppath % self.cprops.name
        with open(fpath) as phys_file:
            chassis.set_z(yaml_load(phys_file)['center_mass_offset'])
        self.load_wheels(chassis)

    def reparent(self):
        self.chassis_np.reparent_to(self.nodepath)
        chas = [self.chassis_np, self.chassis_np_low, self.chassis_np_hi]
        map(lambda cha: cha.set_depth_offset(-2), chas)
        wheels = self.wheels.values()
        map(lambda whl: whl.reparent_to(self.eng.gfx.root), wheels)
        # try RigidBodyCombiner for the wheels
        for cha in chas: cha.optimize()
        self.on_skidmarking()
        self.cnt = 5
        for _ in range(6):
            self.preload_tsk()
            base.graphicsEngine.renderFrame()

    def preload_tsk(self):
        wpn_classes = [Rocket, RearRocket, Turbo, RotateAll, Mine]
        if self.cnt:
            self.apply_damage()
            self.mediator.event.on_bonus(wpn_classes[self.cnt - 1])
            self.cnt -= 1
        else:
            self.apply_damage(True)
            self.mediator.event.on_bonus('remove')

    def load_wheels(self, chassis_model):
        self.chassis_np = chassis_model
        load = self.eng.load_model
        gprops = self.cprops.race_props.season_props.gameprops
        fpath = gprops.wheel_gfx_names.front % self.cprops.name
        rpath = gprops.wheel_gfx_names.rear % self.cprops.name
        m_exists = lambda path: exists(path + '.egg') or exists(path + '.bam')
        b_path = gprops.wheel_gfx_names.both % self.cprops.name
        front_path = fpath if m_exists(fpath) else b_path
        rear_path = rpath if m_exists(rpath) else b_path
        self.wheels['fr'] = load(front_path)
        self.wheels['fl'] = load(front_path)
        self.wheels['rr'] = load(rear_path)
        self.wheels['rl'] = load(rear_path)
        GfxColleague._end_async(self)

    def crash_sfx(self):
        self.crash_cnt += 1
        if self.mediator.phys.prev_speed_ratio < .8 or \
                self.eng.curr_time - self.last_crash_t < 5.0 or \
                self.crash_cnt < 2:
            return False
        pos = self.nodepath.get_pos(self.eng.gfx.root) + (0, 1.2, .75)
        self.eng.particle(self.eng.gfx.root, pos, (0, 0, 0), 'sparkle', 1.6, 1000, (1, 1, 1, .24))
        self.apply_damage()
        level = 0
        curr_chassis = self.nodepath.children[0]
        if self.chassis_np_low.name in curr_chassis.get_name():
            level = 1
        if self.chassis_np_hi.name in curr_chassis.get_name():
            level = 2
        self.mediator.event.on_damage(level)
        return True

    def apply_damage(self, reset=False):
        curr_chassis = self.nodepath.children[0]
        if reset:
            next_chassis = self.chassis_np
        elif self.chassis_np_low.name in curr_chassis.get_name():
            next_chassis = self.chassis_np_hi
        elif self.chassis_np_hi.name in curr_chassis.get_name():
            return
        else:
            next_chassis = self.chassis_np_low
        curr_chassis.remove_node()
        next_chassis.reparent_to(self.nodepath)
        if self.mediator.logic.weapon:
            self.mediator.logic.weapon.reparent(next_chassis)
        self.mediator.phys.apply_damage(reset)
        self.mediator.gui.apply_damage(reset)
        self.last_crash_t = self.eng.curr_time
        self.crash_cnt = 0

    def destroy(self):
        meshes = [self.nodepath, self.chassis_np] + self.wheels.values()
        map(lambda mesh: mesh.remove_node(), meshes)
        map(lambda dec: dec.destroy(), self.decorators)
        self.wheels = self.decorators = None
        self.skidmark_mgr.destroy()
        map(self.eng.rm_do_later, self.dec_tsk)
        GfxColleague.destroy(self)


class CarPlayerGfx(CarGfx):

    def crash_sfx(self):
        if CarGfx.crash_sfx(self):
            self.mediator.audio.crash_high_speed_sfx.play()


class SkidmarkMgr(GameObject):

    def __init__(self, car):
        GameObject.__init__(self)
        self.l_skidmark = self.r_skidmark = None
        self.skidmarks = []
        self.car = car

    def on_skidmarking(self):
        fr_pos = self.car.gfx.wheels['fr'].get_pos(self.eng.gfx.root)
        fl_pos = self.car.gfx.wheels['fl'].get_pos(self.eng.gfx.root)
        heading = self.car.gfx.nodepath.h
        if self.r_skidmark:
            self.r_skidmark.update(fr_pos, heading)
            self.l_skidmark.update(fl_pos, heading)
        else:
            radius = self.car.phys.vehicle.getWheels()[0].getWheelRadius()
            self.r_skidmark = Skidmark(fr_pos, radius, heading)
            self.l_skidmark = Skidmark(fl_pos, radius, heading)
            self.skidmarks += [self.l_skidmark, self.r_skidmark]
            wheels = self.car.phys.vehicle.get_wheels()
            whl_radius = wheels[2].get_wheel_radius()
            whl_pos_l = wheels[2].get_chassis_connection_point_cs() + \
                (0, -whl_radius, -whl_radius + .05)
            whl_pos_r = wheels[3].get_chassis_connection_point_cs() + \
                (0, -whl_radius, -whl_radius + .05)
            self.eng.particle(self.car.gfx.nodepath, whl_pos_l, (0, 60, 0),
                              'dust', 1.2, 100, (.5, .5, .5, .24), pi/12)
            self.eng.particle(self.car.gfx.nodepath, whl_pos_r, (0, 60, 0),
                              'dust', 1.2, 100, (.5, .5, .5, .24), pi/12)

    def on_no_skidmarking(self):
        self.l_skidmark = self.r_skidmark = None

    def destroy(self):
        map(lambda skd: skd.destroy(), self.skidmarks)
        self.car = self.skidmarks = None
        GameObject.destroy(self)
