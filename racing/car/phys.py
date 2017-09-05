from yaml import load
from panda3d.bullet import BulletVehicle, ZUp, BulletConvexHullShape
from panda3d.core import LPoint3f, BitMask32, Mat4
from yyagl.gameobject import Phys
from yyagl.engine.log import LogMgr
from yyagl.engine.phys import PhysMgr


class CarPhys(Phys):

    def __init__(self, mdt, car_props, race_props, season_props):
        Phys.__init__(self, mdt)
        self.pnode = self.vehicle = self.friction_slip = self.__track_phys = \
            self.coll_mesh = self.roll_influence = self.max_speed = None
        self.curr_speed_mul = 1.0
        self.__prev_speed = 0
        self.__last_drift_time = 0
        self.__finds = {}  # cache for find's results
        self.cprops = car_props
        self.rprops = race_props
        self.sprops = season_props
        self._load_phys()
        self.__set_collision_mesh()
        self.__set_phys_node()
        self.__set_vehicle()
        self.__set_wheels()
        self.eng.attach_obs(self.on_end_frame)

    def _load_phys(self):
        fpath = self.rprops.phys_file % self.cprops.name
        with open(fpath) as phys_file:
            self.cfg = load(phys_file)

        # they may be changed by drivers and tuning
        self.cfg['max_speed'] = self.get_speed()
        self.cfg['friction_slip'] = self.get_friction()
        self.cfg['roll_influence'] = self.get_roll_influence()
        self.__log_props()
        set_a = lambda field: setattr(self, field, self.cfg[field])
        map(set_a, self.cfg.keys())

    def __log_props(self, starting=True):
        s_s = self.cfg['max_speed'] if starting else self.max_speed
        s_f = self.cfg['friction_slip'] if starting else self.friction_slip
        s_r = self.cfg['roll_influence'] if starting else self.roll_influence
        log_info = [
            ('speed', self.cprops.name, round(s_s, 2),
             self.cprops.driver_engine),
            ('friction', self.cprops.name, round(s_f, 2),
             self.cprops.driver_tires),
            ('roll', self.cprops.name, round(s_r, 2),
             self.cprops.driver_suspensions)]
        for l_i in log_info:
            self.eng.log_mgr.log('%s %s: %s (%s)' % l_i)

    def __set_collision_mesh(self):
        fpath = self.rprops.coll_path % self.cprops.name
        self.coll_mesh = loader.loadModel(fpath)
        chassis_shape = BulletConvexHullShape()
        for geom in self.eng.phys_mgr.find_geoms(self.coll_mesh,
                                         self.rprops.coll_name):
            chassis_shape.add_geom(geom.node().get_geom(0),
                                   geom.get_transform())
        self.mdt.gfx.nodepath.node().add_shape(chassis_shape)
        car_idx = self.rprops.cars.index(self.cprops.name)
        mask = BitMask32.bit(1) | BitMask32.bit(2 + car_idx)
        self.mdt.gfx.nodepath.set_collide_mask(mask)

    def __set_phys_node(self):
        self.pnode = self.mdt.gfx.nodepath.node()
        self.pnode.set_mass(self.mass)
        self.pnode.set_deactivation_enabled(False)
        self.eng.phys_mgr.attach_rigid_body(self.pnode)
        self.eng.phys_mgr.add_collision_obj(self.pnode)

    def __set_vehicle(self):
        self.vehicle = BulletVehicle(self.eng.phys_mgr.root, self.pnode)
        self.vehicle.set_coordinate_system(ZUp)
        self.vehicle.set_pitch_control(self.pitch_control)
        tuning = self.vehicle.get_tuning()
        tuning.set_suspension_compression(self.suspension_compression)
        tuning.set_suspension_damping(self.suspension_damping)
        self.eng.phys_mgr.attach_vehicle(self.vehicle)

    def __set_wheels(self):
        wheels = self.mdt.gfx.wheels
        f_bounds = wheels['fr'].get_tight_bounds()
        f_radius = (f_bounds[1][2] - f_bounds[0][2]) / 2.0 + .01
        r_bounds = wheels['rr'].get_tight_bounds()
        r_radius = (r_bounds[1][2] - r_bounds[0][2]) / 2.0 + .01
        ffr = self.coll_mesh.find('**/' + self.rprops.wheel_names.frontrear.fr)
        ffl = self.coll_mesh.find('**/' + self.rprops.wheel_names.frontrear.fl)
        rrr = self.coll_mesh.find('**/' + self.rprops.wheel_names.frontrear.rr)
        rrl = self.coll_mesh.find('**/' + self.rprops.wheel_names.frontrear.rl)
        meth = self.coll_mesh.find
        fr_node = ffr if ffr else meth('**/' + self.rprops.wheel_names.both.fr)
        fl_node = ffl if ffl else meth('**/' + self.rprops.wheel_names.both.fl)
        rr_node = rrr if rrr else meth('**/' + self.rprops.wheel_names.both.rr)
        rl_node = rrl if rrl else meth('**/' + self.rprops.wheel_names.both.rl)
        fr_pos = fr_node.get_pos() + (0, 0, f_radius)
        fl_pos = fl_node.get_pos() + (0, 0, f_radius)
        rr_pos = rr_node.get_pos() + (0, 0, r_radius)
        rl_pos = rl_node.get_pos() + (0, 0, r_radius)
        wheels_info = [
            (fr_pos, True, wheels['fr'], f_radius),
            (fl_pos, True, wheels['fl'], f_radius),
            (rr_pos, False, wheels['rr'], r_radius),
            (rl_pos, False, wheels['rl'], r_radius)]
        for (pos, front, nodepath, radius) in wheels_info:
            self.__add_wheel(pos, front, nodepath.node(), radius)

    def __add_wheel(self, pos, is_front, node, radius):
        whl = self.vehicle.create_wheel()
        whl.set_node(node)
        whl.set_chassis_connection_point_cs(LPoint3f(*pos))
        whl.set_front_wheel(is_front)
        whl.set_wheel_direction_cs((0, 0, -1))
        whl.set_wheel_axle_cs((1, 0, 0))
        whl.set_wheel_radius(radius)
        whl.set_suspension_stiffness(self.suspension_stiffness)
        whl.set_wheels_damping_relaxation(self.wheels_damping_relaxation)
        whl.set_wheels_damping_compression(self.wheels_damping_compression)
        whl.set_friction_slip(self.friction_slip)  # high -> more adherence
        whl.set_roll_influence(self.roll_influence)  # low ->  more stability
        whl.set_max_suspension_force(self.max_suspension_force)
        whl.set_max_suspension_travel_cm(self.max_suspension_travel_cm)
        whl.set_skid_info(self.skid_info)

    @property
    def lateral_force(self):
        vel = self.vehicle.get_chassis().get_linear_velocity()
        rot_mat = Mat4()
        rot_mat.setRotateMat(-90, (0, 0, 1))
        car_lat = rot_mat.xformVec(self.mdt.logic.car_vec)
        proj_frc = vel.project(car_lat)
        return proj_frc.length()

    @property
    def is_flying(self):  # no need to be cached
        rays = [whl.get_raycast_info() for whl in self.vehicle.get_wheels()]
        return not any(ray.is_in_contact() for ray in rays)

    @property
    def is_drifting(self):
        return self.lateral_force > 4.0

    @property
    def last_drift_time(self):
        return self.__last_drift_time

    @property
    def prev_speed(self):
        return self.__prev_speed

    @property
    def prev_speed_ratio(self):
        return max(0, min(1.0, self.prev_speed / self.max_speed))

    def on_end_frame(self):
        self.__prev_speed = self.speed

    @property
    def speed(self):
        if self.mdt.fsm.getCurrentOrNextState() == 'Countdown':
            return 0  # getCurrentSpeedKmHour returns odd values otherwise
        return self.vehicle.get_current_speed_km_hour()

    @property
    def speed_ratio(self):
        return max(0, min(1.0, self.speed / self.max_speed))

    def set_forces(self, eng_frc, brake_frc, steering):
        self.vehicle.set_steering_value(steering, 0)
        self.vehicle.set_steering_value(steering, 1)
        self.vehicle.apply_engine_force(eng_frc, 2)
        self.vehicle.apply_engine_force(eng_frc, 3)
        self.vehicle.set_brake(brake_frc, 2)
        self.vehicle.set_brake(brake_frc, 3)

    def update_car_props(self):
        speeds = map(self.__update_whl_props, self.vehicle.get_wheels())
        speeds = [speed for speed in speeds if speed]
        if self.is_drifting:
            self.__last_drift_time = globalClock.get_frame_time()
        self.curr_speed_mul = (sum(speeds) / len(speeds)) if speeds else 1.0

    def __update_whl_props(self, whl):
        contact_pt = whl.get_raycast_info().getContactPointWs()
        gnd_name = self.gnd_name(contact_pt)
        if not gnd_name:
            return
        if gnd_name not in self.__finds:
            gnd = self.cprops.race.track.phys.model.find('**/' + gnd_name)
            self.__finds[gnd_name] = gnd
        gfx_node = self.__finds[gnd_name]
        if gfx_node.has_tag('friction'):
            fric = float(gfx_node.get_tag('friction'))
            whl.setFrictionSlip(self.friction_slip * fric)
        if gfx_node.has_tag('speed'):
            return float(gfx_node.get_tag('speed'))

    @property
    def gnd_names(self):  # no need to be cached
        whls = self.vehicle.get_wheels()
        pos = map(lambda whl: whl.get_raycast_info().get_contact_point_ws(),
                  whls)
        return map(self.gnd_name, pos)

    @staticmethod
    def gnd_name(pos):
        top, bottom = pos + (0, 0, 20), pos + (0, 0, -20)
        result = CarPhys.eng.phys_mgr.ray_test_closest(bottom, top)
        ground = result.get_node()
        return ground.get_name() if ground else ''

    @staticmethod
    def gnd_height(pos):  # this should be a method of the track
        top, bottom = pos + (0, 0, 20), pos + (0, 0, -20)
        result = self.eng.phys_mgr.ray_test_closest(bottom, top)
        hit_pos = result.get_hit_pos()
        return hit_pos.z if hit_pos else None

    def apply_damage(self, reset=False):
        wheels = self.vehicle.get_wheels()
        if reset:
            self.max_speed = self.get_speed()
            self.friction_slip = self.get_friction()
            self.roll_influence = self.get_roll_influence()
        else:
            self.max_speed *= .95
            self.friction_slip *= .95
            self.roll_influence *= 1.05
        map(lambda whl: whl.set_friction_slip(self.friction_slip), wheels)
        map(lambda whl: whl.set_roll_influence(self.roll_influence), wheels)
        self.__log_props(False)

    def get_speed(self):
        return self.cfg['max_speed'] * (1 + .01 * self.cprops.driver_engine)

    def get_friction(self):
        return self.cfg['friction_slip'] * (1 + .01 * self.cprops.driver_tires)

    def get_roll_influence(self):
        return self.cfg['roll_influence'] * (
            1 + .01 * self.cprops.driver_suspensions)

    def rotate(self):
        self.pnode.apply_torque((0, 0, 900000))
        self.mdt.logic.applied_torque = True

    def destroy(self):
        self.eng.detach_obs(self.on_end_frame)
        self.eng.phys_mgr.remove_vehicle(self.vehicle)
        self.pnode = self.vehicle = self.__finds = self.__track_phys = \
            self.coll_mesh = None
        Phys.destroy(self)


class CarPlayerPhys(CarPhys):

    def get_speed(self):
        tun_c = 1 + .1 * self.sprops.tuning_engine
        drv_c = 1 + .01 * self.cprops.driver_engine
        return self.cfg['max_speed'] * tun_c * drv_c

    def get_friction(self):
        tun_c = 1 + .1 * self.sprops.tuning_tires
        drv_c = 1 + .01 * self.cprops.driver_tires
        return self.cfg['friction_slip'] * tun_c * drv_c

    def get_roll_influence(self):
        tun_c = 1 + .1 * self.sprops.tuning_suspensions
        drv_c = 1 + .01 * self.cprops.driver_suspensions
        return self.cfg['roll_influence'] * tun_c * drv_c
