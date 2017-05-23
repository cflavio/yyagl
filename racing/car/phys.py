from yaml import load
from panda3d.bullet import BulletVehicle, ZUp, BulletConvexHullShape,\
    BulletGhostNode, BulletBoxShape, BulletSphereShape, BulletCapsuleShape
from panda3d.core import LPoint3f, BitMask32
from yyagl.gameobject import Phys


class CarPhysProps:

    def __init__(
            self, coll_path, coll_name, track_phys, phys_file, wheel_names,
            tuning_engine, tuning_tires, tuning_suspensions, driver_engine,
            driver_tires, driver_suspensions, cars):
        self.coll_path = coll_path
        self.coll_name = coll_name
        self.track_phys = track_phys
        self.phys_file = phys_file
        self.wheel_names = wheel_names
        self.tuning_engine = tuning_engine
        self.tuning_tires = tuning_tires
        self.tuning_suspensions = tuning_suspensions
        self.driver_engine = driver_engine
        self.driver_tires = driver_tires
        self.driver_suspensions = driver_suspensions
        self.cars = cars


class CarPhys(Phys):

    def __init__(self, mdt, carphys_props):
        Phys.__init__(self, mdt)
        self.pnode = None
        self.vehicle = None
        self.curr_speed_factor = 1.0
        self.__prev_speed = 0
        self.__finds = {}  # cache for find's results
        self.props = carphys_props
        self._load_phys()
        self.__set_collision_mesh()
        self.__set_phys_node()
        self.__set_vehicle()
        self.__set_wheels()
        eng.attach_obs(self.on_end_frame)

    def _load_phys(self):
        fpath = self.props.phys_file % self.mdt.name
        with open(fpath) as phys_file:  # pass phys props as a class
            self.cfg = load(phys_file)
        self.cfg['max_speed'] = self.get_speed()
        self.cfg['friction_slip'] = self.get_friction()
        self.cfg['roll_influence'] = self.get_roll_influence()
        s_a = (self.mdt.name, round(self.cfg['max_speed'], 2),
               self.props.driver_engine)
        eng.log('speed %s: %s (%s)' % s_a)
        fr_slip = round(self.cfg['friction_slip'], 2)
        f_a = (self.mdt.name, fr_slip, self.props.driver_tires)
        eng.log('friction %s: %s (%s)' % f_a)
        r_a = (self.mdt.name, round(self.cfg['roll_influence'], 2),
               self.props.driver_suspensions)
        eng.log('roll %s: %s (%s)' % r_a)
        s_a = lambda field: setattr(self, field, self.cfg[field])
        map(s_a, self.cfg.keys())

    def __set_collision_mesh(self):
        fpath = self.props.coll_path % self.mdt.name
        self.coll_mesh = loader.loadModel(fpath)
        chassis_shape = BulletConvexHullShape()
        for geom in eng.find_geoms(self.coll_mesh, self.props.coll_name):
            chassis_shape.addGeom(geom.node().getGeom(0), geom.getTransform())
        self.mdt.gfx.nodepath.node().addShape(chassis_shape)
        self.mdt.gfx.nodepath.setCollideMask(BitMask32.bit(1) | BitMask32.bit(2 + self.props.cars.index(self.mdt.name)))
        #nodepath = self.mdt.gfx.nodepath.attachNewNode(BulletGhostNode('car ghost'))
        #nodepath.node().addShape(BulletCapsuleShape(4, 5, ZUp))
        #eng.attach_ghost(nodepath.node())
        #nodepath.node().notifyCollisions(False)

    def __set_phys_node(self):
        self.pnode = self.mdt.gfx.nodepath.node()
        self.pnode.setMass(self.mass)
        self.pnode.setDeactivationEnabled(False)
        eng.attach_rigid_body(self.pnode)
        eng.add_collision_obj(self.pnode)

    def __set_vehicle(self):
        self.vehicle = BulletVehicle(eng.phys.world_phys, self.pnode)
        self.vehicle.setCoordinateSystem(ZUp)
        self.vehicle.setPitchControl(self.pitch_control)
        tuning = self.vehicle.getTuning()
        tuning.setSuspensionCompression(self.suspension_compression)
        tuning.setSuspensionDamping(self.suspension_damping)
        eng.attach_vehicle(self.vehicle)

    def __set_wheels(self):
        fwheel_bounds = self.mdt.gfx.wheels['fr'].get_tight_bounds()
        f_radius = (fwheel_bounds[1][2] - fwheel_bounds[0][2]) / 2.0 + .01
        rwheel_bounds = self.mdt.gfx.wheels['rr'].get_tight_bounds()
        r_radius = (rwheel_bounds[1][2] - rwheel_bounds[0][2]) / 2.0 + .01
        ffr = self.coll_mesh.find('**/' + self.props.wheel_names[0][0])
        ffl = self.coll_mesh.find('**/' + self.props.wheel_names[0][1])
        rrr = self.coll_mesh.find('**/' + self.props.wheel_names[0][2])
        rrl = self.coll_mesh.find('**/' + self.props.wheel_names[0][3])
        meth = self.coll_mesh.find
        fr_node = ffr if ffr else meth('**/' + self.props.wheel_names[1][0])
        fl_node = ffl if ffl else meth('**/' + self.props.wheel_names[1][1])
        rr_node = rrr if rrr else meth('**/' + self.props.wheel_names[1][2])
        rl_node = rrl if rrl else meth('**/' + self.props.wheel_names[1][3])
        wheel_fr_pos = fr_node.get_pos() + (0, 0, f_radius)
        wheel_fl_pos = fl_node.get_pos() + (0, 0, f_radius)
        wheel_rr_pos = rr_node.get_pos() + (0, 0, r_radius)
        wheel_rl_pos = rl_node.get_pos() + (0, 0, r_radius)
        frw = self.mdt.gfx.wheels['fr']
        flw = self.mdt.gfx.wheels['fl']
        rrw = self.mdt.gfx.wheels['rr']
        rlw = self.mdt.gfx.wheels['rl']
        wheels_info = [
            (wheel_fr_pos, True, frw, f_radius),
            (wheel_fl_pos, True, flw, f_radius),
            (wheel_rr_pos, False, rrw, r_radius),
            (wheel_rl_pos, False, rlw, r_radius)]
        for (pos, front, nodepath, radius) in wheels_info:
            self.__add_wheel(pos, front, nodepath.node(), radius)

    def __add_wheel(self, pos, front, node, radius):
        whl = self.vehicle.createWheel()
        whl.setNode(node)
        whl.setChassisConnectionPointCs(LPoint3f(*pos))
        whl.setFrontWheel(front)
        whl.setWheelDirectionCs((0, 0, -1))
        whl.setWheelAxleCs((1, 0, 0))
        whl.setWheelRadius(radius)
        whl.setSuspensionStiffness(self.suspension_stiffness)
        whl.setWheelsDampingRelaxation(self.wheels_damping_relaxation)
        whl.setWheelsDampingCompression(self.wheels_damping_compression)
        whl.setFrictionSlip(self.friction_slip)  # high -> more adherence
        whl.setRollInfluence(self.roll_influence)  # low ->  more stability
        whl.setMaxSuspensionForce(self.max_suspension_force)
        whl.setMaxSuspensionTravelCm(self.max_suspension_travel_cm)
        whl.setSkidInfo(self.skid_info)

    @property
    def lateral_force(self):
        vel = self.vehicle.get_chassis().get_linear_velocity()
        vel.normalize()
        dir = self.mdt.logic.car_vec
        lat = dir.dot(vel)
        lat_force = 0
        if lat > .5:
            lat_force = min(1, (lat - 1.0) / -.2)
        return lat_force

    @property
    def is_flying(self):  # no need to be cached
        rays = [whl.getRaycastInfo() for whl in self.vehicle.get_wheels()]
        return not any(ray.isInContact() for ray in rays)

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
        return self.vehicle.getCurrentSpeedKmHour()

    @property
    def speed_ratio(self):
        return max(0, min(1.0, self.speed / self.max_speed))

    def set_forces(self, eng_frc, brake_frc, steering):
        self.vehicle.setSteeringValue(steering, 0)
        self.vehicle.setSteeringValue(steering, 1)
        self.vehicle.applyEngineForce(eng_frc, 2)
        self.vehicle.applyEngineForce(eng_frc, 3)
        self.vehicle.setBrake(brake_frc, 2)
        self.vehicle.setBrake(brake_frc, 3)

    def update_car_props(self):
        speeds = []
        for whl in self.vehicle.get_wheels():
            contact_pt = whl.get_raycast_info().getContactPointWs()
            gnd_name = self.gnd_name(contact_pt)
            if not gnd_name:
                continue
            if gnd_name not in self.__finds:
                gnd = self.props.track_phys.find('**/' + gnd_name)
                self.__finds[gnd_name] = gnd
            gfx_node = self.__finds[gnd_name]
            if gfx_node.has_tag('speed'):
                speeds += [float(gfx_node.get_tag('speed'))]
            if gfx_node.has_tag('friction'):
                fric = float(gfx_node.get_tag('friction'))
                whl.setFrictionSlip(self.friction_slip * fric)
        self.curr_speed_factor = (sum(speeds) / len(speeds)) if speeds else 1.0

    @property
    def gnd_names(self):  # no need to be cached
        whls = self.vehicle.get_wheels()
        pos = map(lambda whl: whl.get_raycast_info().getContactPointWs(), whls)
        return map(self.gnd_name, pos)

    @staticmethod
    def gnd_name(pos):
        top = pos + (0, 0, 20)
        bottom = pos + (0, 0, -20)
        result = eng.ray_test_closest(bottom, top)
        ground = result.get_node()
        return ground.get_name() if ground else ''

    def apply_damage(self, reset=False):
        if reset:
            self.max_speed = self.get_speed()
            self.friction_slip = self.get_friction()
            self.roll_influence = self.get_roll_influence()
        else:
            self.max_speed *= .95
            self.friction_slip *= .95
            self.roll_influence *= 1.05
        fric = lambda whl: whl.setFrictionSlip(self.friction_slip)
        map(fric, self.vehicle.get_wheels())
        roll = lambda whl: whl.setRollInfluence(self.roll_influence)
        map(roll, self.vehicle.get_wheels())
        s_a = (str(round(self.max_speed, 2)), self.props.driver_engine)
        eng.log_mgr.log('speed: %s (%s)' % s_a)
        f_a = (str(round(self.friction_slip, 2)), self.props.driver_tires)
        eng.log_mgr.log('friction: %s (%s)' % f_a)
        r_a = (str(round(self.roll_influence, 2)),
               self.props.driver_suspensions)
        eng.log_mgr.log('roll: %s (%s)' % r_a)

    def get_speed(self):
        return self.cfg['max_speed'] * (1 + .01 * self.props.driver_engine)

    def get_friction(self):
        return self.cfg['friction_slip'] * (1 + .01 * self.props.driver_tires)

    def get_roll_influence(self):
        return self.cfg['roll_influence'] * (
            1 + .01 * self.props.driver_suspensions)

    def destroy(self):
        eng.detach_obs(self.on_end_frame)
        eng.remove_vehicle(self.vehicle)
        self.pnode = self.vehicle = self.__finds = self.__track_phys = \
            self.coll_mesh = None
        Phys.destroy(self)


class CarPlayerPhys(CarPhys):

    def get_speed(self):
        t_c = 1 + .1 * self.props.tuning_engine
        d_c = 1 + .01 * self.props.driver_engine
        return self.cfg['max_speed'] * t_c * d_c

    def get_friction(self):
        t_c = 1 + .1 * self.props.tuning_tires
        d_c = 1 + .01 * self.props.driver_tires
        return self.cfg['friction_slip'] * t_c * d_c

    def get_roll_influence(self):
        t_c = 1 + .1 * self.props.tuning_suspensions
        d_c = 1 + .01 * self.props.driver_suspensions
        return self.cfg['roll_influence'] * t_c * d_c
