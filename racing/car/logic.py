from math import sin, cos, pi
from collections import namedtuple
from panda3d.core import deg2Rad, LPoint3f, Mat4, BitMask32
from yyagl.gameobject import LogicColleague
from yyagl.computer_proxy import ComputerProxy, compute_once, once_a_frame
from yyagl.racing.camera import Camera
from yyagl.racing.weapon.rear_rocket.rear_rocket import RearRocket
from yyagl.engine.vec import Vec2, Vec


WPInfo = namedtuple('WPInfo', 'prev next')


class Input2ForcesStrategy(object):

    @staticmethod
    def build(is_player, joystick, car):
        return (DiscreteInput2ForcesStrategy
                if not joystick or not is_player
                else AnalogicInput2ForcesStrategy)(car)

    def __init__(self, car):
        self._steering = 0  # degrees
        self.car = car
        self.drift = DriftingForce(car)
        self.start_left_t = self.start_right_t = None
        self.curr_clamp = 0
        self.tgt_clamp = 0

    @property
    def steering_inc(self):
        return globalClock.get_dt() * self.car.phys.steering_inc

    @property
    def steering_dec(self):
        return globalClock.get_dt() * self.car.phys.steering_dec

    @staticmethod
    def new_val(val, tgt, incr, decr):
        beyond = abs(val - tgt) < incr
        next_val = lambda: val + (incr if tgt > val else  -decr)
        return tgt if beyond else next_val()

    def steering_clamp(self, is_drifting):
        phys = self.car.phys
        speed_ratio = phys.lin_vel_ratio
        steering_range = phys.steering_min_speed - phys.steering_max_speed
        clamp_incr_speed = globalClock.get_dt() * 16
        clamp_decr_speed = globalClock.get_dt() * 32
        if is_drifting: speed_ratio *= .5
        k = sin(speed_ratio * pi / 2)
        self.tgt_clamp = phys.steering_min_speed - k * steering_range
        self.curr_clamp = self.new_val(self.curr_clamp, self.tgt_clamp, clamp_incr_speed, clamp_decr_speed)
        return self.curr_clamp

    def get_eng_frc(self, eng_frc):
        m_s = self.car.phys.max_speed
        actual_max_speed = m_s * self.car.phys.curr_speed_mul
        eng_frc = eng_frc * (1.05 - self.car.phys.lin_vel / actual_max_speed)
        return eng_frc


class DriftingForce(object):

    def __init__(self, car):
        self.car = car
        self.vel_start = 0

    def process(self, input_dct):
        phys = self.car.phys
        if phys.lin_vel < 10: return
        car_vec = self.car.logic.car_vec
        rot_mat_left = Mat4()
        rot_mat_left.setRotateMat(90, (0, 0, 1))
        car_vec_left = rot_mat_left.xformVec(car_vec)

        rot_mat_drift_left = Mat4()
        rot_mat_drift_left.setRotateMat(45 if input_dct.forward else 90, (0, 0, 1))
        drift_vec_left = rot_mat_drift_left.xformVec(car_vec)

        rot_mat_right = Mat4()
        rot_mat_right.setRotateMat(-90, (0, 0, 1))
        car_vec_right = rot_mat_right.xformVec(car_vec)

        rot_mat_drift_right = Mat4()
        rot_mat_drift_right.setRotateMat(-45 if input_dct.forward else 90, (0, 0, 1))
        drift_vec_right = rot_mat_drift_right.xformVec(car_vec)

        max_intensity = 10000.0
        max_intensity_torque = 5000.0
        intensity = 0
        intensity_torque = 0

        vel = phys.vehicle.get_chassis().get_linear_velocity()
        vel.normalize()

        car_dot_vel_l = car_vec_left.dot(vel)
        car_dot_vel_r = car_vec_right.dot(vel)
        car_dot_vel = max(car_dot_vel_l, car_dot_vel_r)

        if car_dot_vel > .1 and not self.vel_start:
            self.vel_start = phys.vehicle.get_chassis().get_linear_velocity().length()
        elif car_dot_vel <= .1:
            self.vel_start = 0
            return

        vel_fact = self.vel_start - phys.vehicle.get_chassis().get_linear_velocity().length()
        vel_fact /= phys.max_speed
        vel_fact = min(1, max(0, vel_fact))

        if input_dct.left:
            if car_dot_vel_l > 0:
                intensity = max_intensity * car_dot_vel_l * vel_fact
                direction = drift_vec_left
                intensity_torque = max_intensity_torque * car_dot_vel_l * vel_fact
            elif car_dot_vel_r > 0:
                intensity = max_intensity * car_dot_vel_r * vel_fact
                direction = drift_vec_right
        elif input_dct.right:
            if car_dot_vel_r > 0:
                intensity = max_intensity * car_dot_vel_r * vel_fact
                direction = drift_vec_right
                intensity_torque = - max_intensity_torque * car_dot_vel_r * vel_fact
            elif car_dot_vel_l > 0:
                intensity = max_intensity * car_dot_vel_l * vel_fact
                direction = drift_vec_left
        elif input_dct.forward:
            if car_dot_vel_l > 0:
                intensity = max_intensity * car_dot_vel_l * vel_fact
            if car_dot_vel_r > 0:
                intensity = max_intensity * car_dot_vel_r * vel_fact
            direction = car_vec
        for whl in phys.vehicle.get_wheels():
            if not whl.is_front_wheel():
                whl.setFrictionSlip(whl.getFrictionSlip() * (1 + car_dot_vel_l * vel_fact * .002))
        if intensity: phys.pnode.apply_central_force(direction * intensity)
        if intensity_torque:
            phys.pnode.apply_torque((0, 0, intensity_torque))


class DiscreteInput2ForcesStrategy(Input2ForcesStrategy):

    turn_time = .1  # after this time the steering is at its max value

    def input2forces(self, car_input, joystick_mgr, is_drifting):
        phys = self.car.phys
        eng_frc = brake_frc = 0
        f_t = globalClock.get_frame_time()
        if car_input.forward and car_input.rear:
            eng_frc = phys.engine_acc_frc
            brake_frc = phys.brake_frc
        if car_input.forward and not car_input.rear:
            eng_frc = phys.engine_acc_frc
        if car_input.rear and not car_input.forward:
            eng_frc = phys.engine_dec_frc if phys.speed < .05 else 0
            brake_frc = phys.brake_frc
        if not car_input.forward and not car_input.rear:
            brake_frc = phys.eng_brk_frc
        if car_input.left:
            if self.start_left_t is None:
                self.start_left_t = f_t
            steer_fact = min(1, (f_t - self.start_left_t) / self.turn_time)
            self._steering += self.steering_inc * steer_fact
            self._steering = min(self._steering, self.steering_clamp(is_drifting))
        else:
            self.start_left_t = None
        if car_input.right:
            if self.start_right_t is None:
                self.start_right_t = globalClock.getFrameTime()
            steer_fact = min(1, (f_t - self.start_right_t) / self.turn_time)
            self._steering -= self.steering_inc * steer_fact
            self._steering = max(self._steering, -self.steering_clamp(is_drifting))
        else:
            self.start_right_t = None
        if not car_input.left and not car_input.right:
            if abs(self._steering) <= self.steering_dec:
                self._steering = 0
            else:
                steering_sign = (-1 if self._steering > 0 else 1)
                self._steering += steering_sign * self.steering_dec
        self.drift.process(car_input)
        return self.get_eng_frc(eng_frc), brake_frc, self._steering


class AnalogicInput2ForcesStrategy(Input2ForcesStrategy):

    def input2forces(self, car_input, joystick_mgr, is_drifting):
        phys = self.car.phys
        eng_frc = brake_frc = 0
        j_x, j_y, j_a, j_b = joystick_mgr.get_joystick()
        scale = lambda val: min(1, max(-1, val * 1.2))
        j_x, j_y = scale(j_x), scale(j_y)
        if j_y <= - .1:
            eng_frc = phys.engine_acc_frc * abs(j_y)
        if j_y >= .1:
            eng_frc = phys.engine_dec_frc if phys.speed < .05 else 0
            brake_frc = phys.brake_frc * j_y
        if -.1 <= j_y <= .1:
            brake_frc = phys.eng_brk_frc
        if j_x < -.1:
            self._steering += self.steering_inc * abs(j_x)
            self._steering = min(self._steering, self.steering_clamp(is_drifting))
        if j_x > .1:
            self._steering -= self.steering_inc * j_x
            self._steering = max(self._steering, -self.steering_clamp(is_drifting))
        if -.1 < j_x < .1:
            if abs(self._steering) <= self.steering_dec:
                self._steering = 0
            else:
                steering_sign = (-1 if self._steering > 0 else 1)
                self._steering += steering_sign * self.steering_dec
        return self.get_eng_frc(eng_frc), brake_frc, self._steering


class CarLogic(LogicColleague, ComputerProxy):

    def __init__(self, mediator, car_props):
        LogicColleague.__init__(self, mediator)
        ComputerProxy.__init__(self)
        self.cprops = car_props
        self.lap_time_start = 0
        self.last_roll_ok_time = globalClock.get_frame_time()
        self.last_roll_ko_time = globalClock.get_frame_time()
        self.lap_times = []
        self.__pitstop_wps = {}
        self.__grid_wps = {}
        self.collected_wps = []  # for validating laps
        self.weapon = None
        self.fired_weapons = []
        self.camera = None
        self._grid_wps = self._pitstop_wps = None
        self.input_strat = Input2ForcesStrategy.build(
            self.__class__ == CarPlayerLogic, car_props.race_props.joystick,
            self.mediator)
        self.start_pos = car_props.pos
        self.start_pos_hpr = car_props.hpr
        self.last_ai_wp = None
        for w_p in car_props.track_waypoints:
            self.nogrid_wps(w_p)
        for w_p in car_props.track_waypoints:
            self.nopitlane_wps(w_p)
        self.__wp_num = None
        self.applied_torque = False  # applied from weapons
        self.alt_jmp_wp = None

    def update(self, input2forces):
        phys = self.mediator.phys
        eng_f, brake_f, steering = self.input_strat.input2forces(input2forces, self.eng.joystick_mgr, self.is_drifting)
        phys.set_forces(eng_f, brake_f, steering)
        self.__update_roll_info()
        gfx = self.mediator.gfx
        is_skid = self.is_skidmarking
        gfx.on_skidmarking() if is_skid else gfx.on_no_skidmarking()

    def __update_roll_info(self):
        status = 'ok' if -45 <= self.mediator.gfx.nodepath.get_r() < 45 else 'ko'
        curr_t = globalClock.get_frame_time()
        setattr(self, 'last_roll_%s_time' % status, curr_t)

    def reset_car(self):
        if self.mediator.fsm.getCurrentOrNextState() in ['Off', 'Loading']:
            self.mediator.gfx.nodepath.set_z(self.start_pos[2] + 1.2)
        self.mediator.gfx.nodepath.set_x(self.start_pos[0])
        self.mediator.gfx.nodepath.set_y(self.start_pos[1])
        self.mediator.gfx.nodepath.set_hpr(self.start_pos_hpr)
        wheels = self.mediator.phys.vehicle.get_wheels()
        map(lambda whl: whl.set_rotation(0), wheels)

    @property
    def is_drifting(self):
        car_vec = self.car_vec
        rot_mat_left = Mat4()
        rot_mat_left.setRotateMat(90, (0, 0, 1))
        car_vec_left = rot_mat_left.xformVec(car_vec)
        rot_mat_right = Mat4()
        rot_mat_right.setRotateMat(-90, (0, 0, 1))
        car_vec_right = rot_mat_right.xformVec(car_vec)
        vel = self.mediator.phys.vehicle.get_chassis().get_linear_velocity()
        vel.normalize()
        car_dot_vel_l = car_vec_left.dot(vel)
        car_dot_vel_r = car_vec_right.dot(vel)
        car_dot_vel = max(car_dot_vel_l, car_dot_vel_r)
        return car_dot_vel > .1

    @property
    def pitstop_wps(self):
        # it returns the waypoints of the pitlane
        wps = self.cprops.track_waypoints
        start_forks = [w_p for w_p in wps if len(wps[w_p]) > 1]

        def parents(w_p):
            return [pwp for pwp in wps if w_p in wps[pwp]]
        end_forks = [w_p for w_p in wps if len(parents(w_p)) > 1]
        pitstop_forks = []
        for w_p in start_forks:
            for start in wps[w_p][:]:
                to_process = [start]
                is_pit_stop = False
                try_forks = []
                while to_process:
                    next_wp = to_process.pop(0)
                    try_forks += [next_wp]
                    for nwp in wps[next_wp]:
                        if nwp not in end_forks:
                            to_process += [nwp]
                        if 'PitStop' in self.__get_hits(next_wp, nwp):
                            is_pit_stop = True
                if is_pit_stop:
                    pitstop_forks += try_forks
        return pitstop_forks

    @property
    def grid_wps(self):
        wps = self.cprops.track_waypoints
        start_forks = [w_p for w_p in wps if len(wps[w_p]) > 1]

        def parents(w_p):
            return [pwp for pwp in wps if w_p in wps[pwp]]
        end_forks = [w_p for w_p in wps if len(parents(w_p)) > 1]
        grid_forks = []
        for w_p in start_forks:
            for start in wps[w_p][:]:
                to_process = [start]
                is_grid = False
                is_pitstop = False
                try_forks = []
                while to_process:
                    next_wp = to_process.pop(0)
                    try_forks += [next_wp]
                    for nwp in wps[next_wp]:
                        if nwp not in end_forks:
                            to_process += [nwp]
                        if 'Goal' in self.__get_hits(next_wp, nwp):
                            is_grid = True
                        if 'PitStop' in self.__get_hits(next_wp, nwp):
                            is_pitstop = True
                if is_grid and not is_pitstop:
                    grid_forks += try_forks
        return grid_forks

    @staticmethod
    def __get_hits(wp1, wp2):
        return [
            hit.get_node().get_name()
            for hit in CarLogic.eng.phys_mgr.ray_test_all(
                wp1.get_pos(), wp2.get_pos()).get_hits()]

    @compute_once
    def nogrid_wps(self, curr_wp):
        wps = self.cprops.track_waypoints.copy()
        if curr_wp not in self.grid_wps:
            for _wp in self.grid_wps:
                del wps[_wp]
        return wps

    def nopitlane_wps(self, curr_wp):
        if curr_wp in self.__grid_wps:
            return self.__grid_wps[curr_wp]
        wps = self.cprops.track_waypoints.copy()
        if curr_wp not in self.pitstop_wps:
            for _wp in self.pitstop_wps:
                del wps[_wp]
        self.__grid_wps[curr_wp] = wps
        return wps

    def last_wp_not_fork(self):
        # make a Waypoint class which contains the nodepath and facades stuff
        for pwp in reversed(self.collected_wps):
            _wp = [__wp for __wp in self.cprops.track_waypoints
                   if __wp.get_name()[8:] == str(pwp)][0]  # facade wp's name
            if _wp in self.not_fork_wps():
                return _wp
        if self.not_fork_wps():  # if the track has a goal
            return self.not_fork_wps()[-1]

    @compute_once
    def not_fork_wps(self):
        # waypoints that are not on a fork
        goal_wp = None
        wps = self.cprops.track_waypoints
        for curr_wp in wps:
            for next_wp in wps[curr_wp]:
                hits = self.__get_hits(curr_wp, next_wp)
                if 'Goal' in hits and 'PitStop' not in hits:
                    goal_wp = next_wp

        def parents(w_p):
            return [_wp for _wp in self.cprops.track_waypoints
                    if w_p in self.cprops.track_waypoints[_wp]]
        wps = []
        if not goal_wp:
            return wps
        processed = [goal_wp]
        while any(pwp not in processed for pwp in parents(processed[-1])):
            pwp = [pwp for pwp in parents(processed[-1])
                   if pwp not in processed][0]
            processed += [pwp]
            while pwp in self.__fork_wp():
                may_succ = [_wp for _wp in parents(pwp)
                            if _wp not in processed]
                if not may_succ:
                    break
                processed += [may_succ[0]]
            if pwp not in self.__fork_wp():
                wps += [pwp]
        return wps

    def __log_wp_info(self, curr_chassis, curr_wp, closest_wps, waypoints):
        print self.mediator.name
        print self.mediator.gfx.chassis_np_hi.get_name(), curr_chassis.get_name()
        print len(self.mediator.logic.lap_times), self.mediator.laps - 1
        print self.last_ai_wp, '\n', curr_wp, '\n', closest_wps
        import pprint
        to_print = [waypoints, self._pitstop_wps, self._grid_wps,
                    self.cprops.track_waypoints]
        map(pprint.pprint, to_print)

    @property
    @compute_once
    def bitmask(self):
        b_m = BitMask32.bit(0) | BitMask32.bit(1)
        cars_idx = range(len(self.cprops.race_props.season_props.car_names))
        cars_idx.remove(
            self.cprops.race_props.season_props.car_names.index(self.mediator.name))
        for bitn in cars_idx:
            b_m = b_m | BitMask32.bit(2 + bitn)
        return b_m

    @property
    def has_rear_weapon(self):
        return self.mediator.logic.weapon and \
            self.mediator.logic.weapon.__class__ == RearRocket

    @property
    def curr_chassis(self):
        return self.mediator.gfx.nodepath.get_children()[0]

    @property
    def curr_chassis_name(self):
        return self.curr_chassis.get_name()

    @property
    def hi_chassis_name(self):
        return self.mediator.gfx.chassis_np_hi.get_name()

    @once_a_frame
    def closest_wp(self):
        w2p = self.cprops.track_waypoints
        closest_wps = w2p.keys()
        if self.last_ai_wp:
            closest_wps = [self.last_ai_wp] + \
                w2p[self.last_ai_wp] + \
                [wp for wp in w2p if self.last_ai_wp in w2p[wp]]
        not_last = len(self.mediator.logic.lap_times) < self.mediator.laps - 1
        car_np = self.mediator.gfx.nodepath
        distances = [car_np.get_distance(wp) for wp in closest_wps]
        curr_wp = closest_wps[distances.index(min(distances))]
        self._pitstop_wps = self.nogrid_wps(curr_wp)
        self._grid_wps = self.nopitlane_wps(curr_wp)
        considered_wps = self._pitstop_wps.items() \
            if self.hi_chassis_name in self.curr_chassis_name and not_last \
            else self._grid_wps.items()
        waypoints = {
            wp[0]: wp[1] for wp in considered_wps if wp[0] in closest_wps
            or any(_wp in closest_wps for _wp in wp[1])}
        distances = [car_np.get_distance(wp) for wp in waypoints.keys()]
        if not distances:  # there is a bug
            self.__log_wp_info(self.curr_chassis, curr_wp, closest_wps,
                               waypoints)
        dist_lst = zip(waypoints.keys(), distances)
        curr_wp = min(dist_lst, key=lambda pair: pair[1])[0]
        if self.alt_jmp_wp:
            dist_wp = (car_np.get_pos() - curr_wp.get_pos()).length()
            dist_alt = (car_np.get_pos() - self.alt_jmp_wp.get_pos()).length()
            dist_h_wp = abs(car_np.get_z() - curr_wp.get_z())
            dist_h_alt = abs(car_np.get_z() - self.alt_jmp_wp.get_z())
            if dist_wp > .5 * dist_alt and dist_h_wp > 1.5 * dist_h_alt:
                curr_wp = self.alt_jmp_wp
                waypoints[curr_wp] = self._grid_wps[curr_wp]
        for cons_wp in considered_wps:
            if curr_wp in cons_wp[1]:
                waypoints[cons_wp[0]] = cons_wp[1]
        may_prev = waypoints[curr_wp]
        distances = [self.pt_line_dst(car_np, w_p, curr_wp)
                     for w_p in may_prev]
        if not distances:  # there is a bug
            self.__log_wp_info(self.curr_chassis, curr_wp, closest_wps,
                               waypoints)
        prev_wp = may_prev[distances.index(min(distances))]
        may_succ = [w_p for w_p in waypoints if curr_wp in waypoints[w_p]]
        if len(may_succ) >= 2:
            if any(wp.has_tag('jump') for wp in may_succ):
                cha_name = self.mediator.gfx.chassis_np.get_name()
                if cha_name in self.curr_chassis_name:
                    may_succ = [wp for wp in may_succ if wp.has_tag('jump')]
                    if not self.alt_jmp_wp:
                        jmp_wp_str = may_succ[0].get_tag('jump')
                        for cwp in self._grid_wps.keys():
                            if cwp.get_name() == 'Waypoint' + jmp_wp_str:
                                self.alt_jmp_wp = cwp
                else:
                    may_succ = [wp for wp in may_succ
                                if not wp.has_tag('jump')]
        distances = [self.pt_line_dst(car_np, curr_wp, w_p)
                     for w_p in may_succ]
        if not distances:  # there is a bug
            self.__log_wp_info(self.curr_chassis, curr_wp, closest_wps,
                               waypoints)
        next_wp = may_succ[distances.index(min(distances))]
        if len(self._grid_wps[curr_wp]) >= 2:
            self.alt_jmp_wp = None
        curr_vec = Vec2(*car_np.get_pos(curr_wp).xy).normalize()
        prev_vec = Vec2(*car_np.get_pos(prev_wp).xy).normalize()
        next_vec = Vec2(*car_np.get_pos(next_wp).xy).normalize()
        prev_angle = prev_vec.signed_angle_deg(curr_vec)
        next_angle = next_vec.signed_angle_deg(curr_vec)
        if min(distances) > 10 and abs(prev_angle) > abs(next_angle):
            start_wp, end_wp = prev_wp, curr_wp
        else:
            start_wp, end_wp = curr_wp, next_wp
        self.last_ai_wp = end_wp
        return WPInfo(start_wp, end_wp)

    def update_waypoints(self):
        closest_wp = int(self.closest_wp()[0].get_name()[8:])  # WaypointX
        # facade: wp.num in Waypoint's class
        if closest_wp not in self.collected_wps:
            self.collected_wps += [closest_wp]
            self.__recompute_wp_num()

    def reset_waypoints(self):
        self.collected_wps = []
        self.__recompute_wp_num()

    def __fork_wp(self):
        wps = self.cprops.track_waypoints
        in_forks, start_forks = [], []
        for w_p in wps:
            if len(wps[w_p]) > 1:
                start_forks += [w_p]
        end_forks = []
        for w_p in wps:
            cnt_parents = 0
            for w_p1 in wps:
                if w_p in wps[w_p1]:
                    cnt_parents += 1
            if cnt_parents > 1:
                end_forks += [w_p]
        for w_p in start_forks:
            to_process = wps[w_p][:]
            while to_process:
                first_wp = to_process.pop(0)
                in_forks += [first_wp]
                for w_p2 in wps[first_wp]:
                    if w_p2 not in end_forks:
                        to_process += [w_p2]
        return in_forks

    @property
    def wp_num(self):
        return self.__wp_num

    def __recompute_wp_num(self):  # wp_num is used for ranking
        self.__wp_num = len(
            [vwp for vwp in self.collected_wps if vwp in [
                int(wp.get_name()[8:]) for wp in self.not_fork_wps()]])

    @property
    def correct_lap(self):
        wps = self.cprops.track_waypoints
        all_wp = [int(w_p.get_name()[8:]) for w_p in wps]
        f_wp = [int(w_p.get_name()[8:]) for w_p in self.__fork_wp()]
        map(all_wp.remove, f_wp)
        is_correct = all(w_p in self.collected_wps for w_p in all_wp)
        if not is_correct:
            skipped = [str(w_p) for w_p in all_wp
                       if w_p not in self.collected_wps]
            self.eng.log_mgr.log('skipped waypoints: ' + ', '.join(skipped))
        return is_correct

    @staticmethod
    def pt_line_dst(point, line_pt1, line_pt2):
        # distance of a point from a line
        diff1 = line_pt2.get_pos() - line_pt1.get_pos()
        diff2 = line_pt1.get_pos() - point.get_pos()
        diff = abs(diff1.cross(diff2).length())
        return diff / abs(diff1.length())

    @property
    def car_vec(self):  # port (or add) this to 3D
        car_rad = deg2Rad(self.mediator.gfx.nodepath.get_h())
        return Vec(-sin(car_rad), cos(car_rad), 0).normalize()

    @property
    def direction(self):
        # car's direction dot current direction
        start_wp, end_wp = self.closest_wp()
        wp_vec = Vec(end_wp.get_pos(start_wp).x, end_wp.get_pos(start_wp).y, 0).normalize()
        return self.car_vec.dot(wp_vec)

    @property
    def is_upside_down(self):
        return globalClock.get_frame_time() - self.last_roll_ok_time > 5.0

    @property
    def is_rolling(self):
        return globalClock.get_frame_time() - self.last_roll_ko_time < 1.0

    @property
    def is_rotating(self):
        if self.applied_torque and \
                self.mediator.phys.pnode.get_angular_velocity().length() < .5:
            self.applied_torque = False
        return self.applied_torque

    @property
    def is_skidmarking(self):
        hspeed = self.mediator.phys.speed > 50.0
        flying = self.mediator.phys.is_flying
        input_dct = self.mediator.event._get_input()
        return input_dct.rear and hspeed and not flying

    @property
    def lap_time(self):
        return globalClock.get_frame_time() - self.lap_time_start

    @property
    def laps_num(self):
        return len(self.lap_times)

    def fire(self):
        self.weapon.attach_obs(self.on_weapon_destroyed)
        self.weapon.fire(False)
        self.fired_weapons += [self.weapon]
        self.weapon = None
        self.fired_weapons = [wpn for wpn in self.fired_weapons if wpn]

    def unset_fired_weapon(self, wpn):
        self.fired_weapons.remove(wpn)

    def on_weapon_destroyed(self, wpn):
        if wpn in self.fired_weapons: self.fired_weapons.remove(wpn)
        if wpn != self.weapon: return
        self.weapon.detach_obs(self.mediator.event.on_rotate_all)
        self.weapon.detach_obs(self.on_weapon_destroyed)
        self.weapon = None

    def set_damage(self, level):
        curr_chassis = self.mediator.gfx.nodepath.get_children()[0]
        curr_level = 0
        if self.mediator.gfx.chassis_np_low.get_name() in curr_chassis.get_name():
            curr_level = 1
        elif self.mediator.gfx.chassis_np_hi.get_name() in curr_chassis.get_name():
            curr_level = 2
        if level == 0:
            self.mediator.gfx.apply_damage(True)
        elif level == 1 and curr_level == 0:
            self.mediator.gfx.apply_damage()
        elif level == 2 and curr_level == 1:
            self.mediator.gfx.apply_damage()

    def destroy(self):
        self.camera = None
        if self.weapon: self.weapon = self.weapon.destroy()
        f_wpn = [wpn for wpn in self.fired_weapons if wpn]
        map(lambda wpn: wpn.destroy(), f_wpn)
        self.fired_weapons = []
        LogicColleague.destroy(self)
        ComputerProxy.destroy(self)


class CarPlayerLogic(CarLogic):

    def __init__(self, mediator, car_props):
        CarLogic.__init__(self, mediator, car_props)
        self.camera = Camera(mediator.gfx.nodepath, car_props.race_props.camera_vec, self.mediator)
        start_pos = self.start_pos + (0, 0, 10000)
        self.eng.do_later(.01, self.camera.camera.set_pos, [start_pos])
        self.car_positions = []
        self.last_upd_dist_time = 0
        self.is_moving = True

    def _update_dist(self):
        if self.mediator.fsm.getCurrentOrNextState() in ['Loading', 'Countdown']:
            return
        curr_time = globalClock.get_frame_time()
        if curr_time - self.last_upd_dist_time < 1:
            return
        self.last_upd_dist_time = curr_time
        self.car_positions += [self.mediator.gfx.nodepath.get_pos()]
        if len(self.car_positions) <= 12:
            return
        self.car_positions.pop(0)
        positions = self.car_positions
        center = [sum([pos[idx] for pos in positions]) / len(positions)
                  for idx in range(3)]
        center = LPoint3f(*center)
        self.is_moving = not all((pos - center).length() < 6
                                 for pos in positions)

    def update(self, input_dct):
        CarLogic.update(self, input_dct)
        if self.mediator.fsm.getCurrentOrNextState() == 'Results':
            return
        if self.lap_time_start:
            f_t = globalClock.get_frame_time()
            d_t = round(f_t - self.lap_time_start, 2)
            self.mediator.gui.panel.time_txt.setText(str(d_t))
        if self.lap_time_start:
            self.mediator.gui.panel.speed_txt.setText(str(int(self.mediator.phys.speed)))
        self.__check_wrong_way()
        self._update_dist()
        self.__update_direction_gui()

    def __update_direction_gui(self):
        curr_wp = self.closest_wp().prev.node
        curr_dir = None
        if curr_wp.has_tag('direction'):
            curr_dir = curr_wp.get_tag('direction')
        if curr_dir: self.mediator.gui.show_forward()
        else: self.mediator.gui.hide_forward()

    def fire(self):
        self.weapon.attach_obs(self.on_weapon_destroyed)
        self.weapon.fire(True)
        self.fired_weapons += [self.weapon]
        self.weapon = None
        self.fired_weapons = [wpn for wpn in self.fired_weapons if wpn]

    def __check_wrong_way(self):
        if self.cprops.track_waypoints:
            way_str = _('wrong way') if self.direction < -.6 else ''
            self.mediator.event.notify('on_wrong_way', way_str)
