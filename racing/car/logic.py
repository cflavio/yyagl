from panda3d.core import Vec3, Vec2, deg2Rad
from yyagl.gameobject import Logic
from yyagl.racing.camera import Camera
import math


class AbsLogic(object):

    @staticmethod
    def build(cls, phys):
        not_j = not game.options['settings']['joystick']
        if not_j or cls != CarPlayerLogic:
            return DiscreteLogic(phys)
        else:
            return AnalogicLogic(phys)

    def __init__(self, phys):
        self._steering = 0  # degrees
        self.phys = phys

    @property
    def steering_inc(self):
        return globalClock.getDt() * self.phys.steering_inc

    @property
    def steering_dec(self):
        return globalClock.getDt() * self.phys.steering_dec

    @property
    def steering_clamp(self):
        phys = self.phys
        speed_ratio = phys.speed_ratio
        steering_range = phys.steering_min_speed - phys.steering_max_speed
        return phys.steering_min_speed - speed_ratio * steering_range


class DiscreteLogic(AbsLogic):

    turn_time = .1  # turn time with keyboard

    def process(self, input_dct, phys):
        eng_frc = brake_frc = 0
        f_t = globalClock.getFrameTime()
        if input_dct['forward'] and input_dct['reverse']:
            eng_frc = phys.engine_acc_frc
            brake_frc = phys.brake_frc
        if input_dct['forward'] and not input_dct['reverse']:
            eng_frc = phys.engine_acc_frc
            brake_frc = 0
        if input_dct['reverse'] and not input_dct['forward']:
            eng_frc = phys.engine_dec_frc if phys.speed < .05 else 0
            brake_frc = phys.brake_frc
        if not input_dct['forward'] and not input_dct['reverse']:
            brake_frc = phys.eng_brk_frc
        if input_dct['left']:
            if self.start_left is None:
                self.start_left = f_t
            mul = min(1, (f_t - self.start_left) / self.turn_time)
            self._steering += self.steering_inc * mul
            self._steering = min(self._steering, self.steering_clamp)
        else:
            self.start_left = None
        if input_dct['right']:
            if self.start_right is None:
                self.start_right = globalClock.getFrameTime()
            mul = min(1, (f_t - self.start_right) / self.turn_time)
            self._steering -= self.steering_inc * mul
            self._steering = max(self._steering, -self.steering_clamp)
        else:
            self.start_right = None
        if not input_dct['left'] and not input_dct['right']:
            if abs(self._steering) <= self.steering_dec:
                self._steering = 0
            else:
                steering_sign = (-1 if self._steering > 0 else 1)
                self._steering += steering_sign * self.steering_dec
        return eng_frc, brake_frc, self._steering


class AnalogicLogic(AbsLogic):

    def process(self, input_dct, phys):
        eng_frc = brake_frc = 0
        x, y, a, b = eng.event.joystick.get_joystick()
        scale = lambda val: min(1, max(-1, val * 1.2))
        x, y = scale(x), scale(y)
        if y <= - .1:
            eng_frc = phys.engine_acc_frc * abs(y)
            brake_frc = 0
        if y >= .1:
            eng_frc = phys.engine_dec_frc if phys.speed < .05 else 0
            brake_frc = phys.brake_frc * y
        if -.1 <= y <= .1:
            brake_frc = phys.eng_brk_frc
        if x < -.1:
            self._steering += self.steering_inc * abs(x)
            self._steering = min(self._steering, self.steering_clamp)
        if x > .1:
            self._steering -= self.steering_inc * x
            self._steering = max(self._steering, -self.steering_clamp)
        if -.1 < x < .1:
            if abs(self._steering) <= self.steering_dec:
                self._steering = 0
            else:
                steering_sign = (-1 if self._steering > 0 else 1)
                self._steering += steering_sign * self.steering_dec
        return eng_frc, brake_frc, self._steering


class CarLogic(Logic):

    def __init__(self, mdt, start_pos, start_pos_hpr):
        Logic.__init__(self, mdt)
        self.last_time_start = 0
        self.last_roll_ok_time = globalClock.getFrameTime()
        self.last_roll_ko_time = globalClock.getFrameTime()
        self.lap_times = []
        self.start_left = None
        self.start_right = None
        self.waypoints = []  # collected waypoints for validating laps
        self.weapon = None
        self.input_logic = AbsLogic.build(self.__class__, self.mdt.phys)
        self.start_pos = start_pos
        self.start_pos_hpr = start_pos_hpr
        eng.event.attach(self.on_start_frame)

    def update(self, input_dct):
        phys = self.mdt.phys
        eng_f, brake_f, steering = self.input_logic.process(input_dct, phys)
        phys.set_forces(self.get_eng_frc(eng_f), brake_f, steering)
        self.__update_roll_info()
        gfx = self.mdt.gfx
        is_skid = self.is_skidmarking
        gfx.on_skidmarking() if is_skid else gfx.on_no_skidmarking()

    def get_eng_frc(self, eng_frc):
        m_s = self.mdt.phys.max_speed
        curr_max_speed = m_s * self.mdt.phys.curr_speed_factor
        if self.mdt.phys.speed / curr_max_speed < .99:
            return eng_frc
        tot = .01 * curr_max_speed
        return eng_frc * min(1, (curr_max_speed - self.mdt.phys.speed) / tot)

    def __update_roll_info(self):
        if -45 <= self.mdt.gfx.nodepath.getR() < 45:
            self.last_roll_ok_time = globalClock.getFrameTime()
        else:
            self.last_roll_ko_time = globalClock.getFrameTime()

    def reset_car(self):
        self.mdt.gfx.nodepath.set_pos(self.start_pos)
        self.mdt.gfx.nodepath.set_hpr(self.start_pos_hpr)
        wheels = self.mdt.phys.vehicle.get_wheels()
        map(lambda whl: whl.set_rotation(0), wheels)

    def on_start_frame(self):
        self.__start_wp = None
        self.__end_wp = None

    def closest_wp(self):
        if self.__start_wp:  # do a decorator @once_per_frame
            return self.__start_wp, self.__end_wp
        node = self.mdt.gfx.nodepath
        waypoints = game.track.phys.waypoints
        distances = [node.getDistance(wp) for wp in waypoints.keys()]
        curr_wp = waypoints.keys()[distances.index(min(distances))]
        may_prev = waypoints[curr_wp]
        distances = [self.pt_line_dst(node, w_p, curr_wp) for w_p in may_prev]
        prev_wp = may_prev[distances.index(min(distances))]
        may_succ = [w_p for w_p in waypoints if curr_wp in waypoints[w_p]]
        distances = [self.pt_line_dst(node, curr_wp, w_p) for w_p in may_succ]
        next_wp = may_succ[distances.index(min(distances))]
        curr_vec = Vec2(node.getPos(curr_wp).xy)
        curr_vec.normalize()
        prev_vec = Vec2(node.getPos(prev_wp).xy)
        prev_vec.normalize()
        next_vec = Vec2(node.getPos(next_wp).xy)
        next_vec.normalize()
        prev_angle = prev_vec.signedAngleDeg(curr_vec)
        next_angle = next_vec.signedAngleDeg(curr_vec)
        if abs(prev_angle) > abs(next_angle):
            start_wp, end_wp = prev_wp, curr_wp
        else:
            start_wp, end_wp = curr_wp, next_wp
        self.__start_wp = start_wp
        self.__end_wp = end_wp
        return start_wp, end_wp

    def update_waypoints(self):
        closest_wp = int(self.closest_wp()[0].get_name()[8:])
        if closest_wp not in self.waypoints:
            self.waypoints += [closest_wp]

    def reset_waypoints(self):
        self.waypoints = []

    def __fork_wp(self):
        in_forks = []
        start_forks = []
        for w_p in game.track.phys.waypoints:
            if len(game.track.phys.waypoints[w_p]) > 1:
                start_forks += [w_p]
        end_forks = []
        for w_p in game.track.phys.waypoints:
            count_parents = 0
            for w_p1 in game.track.phys.waypoints:
                if w_p in game.track.phys.waypoints[w_p1]:
                    count_parents += 1
            if count_parents > 1:
                end_forks += [w_p]
        for w_p in start_forks:
            to_process = game.track.phys.waypoints[w_p][:]
            while to_process:
                first_wp = to_process.pop(0)
                in_forks += [first_wp]
                for w_p2 in game.track.phys.waypoints[first_wp]:
                    if w_p2 not in end_forks:
                        to_process += [w_p2]
        return in_forks

    @property
    def correct_lap(self):
        all_wp = [int(w_p.get_name()[8:]) for w_p in game.track.phys.waypoints]
        f_wp = [int(w_p.get_name()[8:]) for w_p in self.__fork_wp()]
        map(all_wp.remove, f_wp)
        is_correct = all(w_p in self.waypoints for w_p in all_wp)
        if not is_correct:
            skipped = [str(w_p) for w_p in all_wp if w_p not in self.waypoints]
            eng.log_mgr.log('skipped waypoints: ' + ', '.join(skipped))
        return is_correct

    @staticmethod
    def pt_line_dst(point, line_pt1, line_pt2):
        diff1 = line_pt2.get_pos() - line_pt1.get_pos()
        diff2 = line_pt1.get_pos() - point.get_pos()
        diff = abs(diff1.cross(diff2).length())
        return diff / abs(diff1.length())

    @property
    def car_vec(self):
        car_rad = deg2Rad(self.mdt.gfx.nodepath.getH())
        car_vec = Vec3(-math.sin(car_rad), math.cos(car_rad), 0)
        car_vec.normalize()
        return car_vec

    @property
    def direction(self):
        start_wp, end_wp = self.closest_wp()
        wp_vec = Vec3(end_wp.getPos(start_wp).xy, 0)
        wp_vec.normalize()
        return self.car_vec.dot(wp_vec)

    @property
    def is_upside_down(self):
        return globalClock.getFrameTime() - self.last_roll_ok_time > 5.0

    @property
    def is_rolling(self):
        return globalClock.getFrameTime() - self.last_roll_ko_time < 1.0

    @property
    def is_skidmarking(self):
        hspeed = self.mdt.phys.speed > 50.0
        flying = self.mdt.phys.is_flying
        input_dct = self.mdt.event._get_input()
        return input_dct['reverse'] and hspeed and not flying

    def destroy(self):
        self.camera = None
        if self.weapon:
            self.weapon = self.weapon.destroy()
        eng.event.detach(self.on_start_frame)
        Logic.destroy(self)


class CarPlayerLogic(CarLogic):

    def __init__(self, mdt, start_pos, start_pos_hpr):
        CarLogic.__init__(self, mdt, start_pos, start_pos_hpr)
        self.camera = Camera(mdt)

    def update(self, input_dct):
        CarLogic.update(self, input_dct)
        if self.mdt.fsm.getCurrentOrNextState() == 'Results':
            return
        if self.last_time_start:
            f_t = globalClock.getFrameTime()
            d_t = round(f_t - self.last_time_start, 2)
            self.mdt.gui.time_txt.setText(str(d_t))
        if self.last_time_start:
            self.mdt.gui.speed_txt.setText(str(int(self.mdt.phys.speed)))
        self.__check_wrong_way()
        ranking = game.fsm.race.logic.ranking()
        r_i = ranking.index(self.mdt.path[5:]) + 1
        self.mdt.gui.ranking_txt.setText(str(r_i) + "'")

    def fire(self):
        self.weapon.logic.fire()

    @property
    def lap_time(self):
        return globalClock.getFrameTime() - self.last_time_start

    def __check_wrong_way(self):
        if game.track.phys.waypoints:
            way_str = _('wrong way') if self.direction < -.6 else ''
            self.notify('on_wrong_way', way_str)
