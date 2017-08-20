from random import uniform
from collections import namedtuple
from panda3d.core import Vec3, Mat4, BitMask32, LineSegs, LPoint3f
from yyagl.gameobject import Ai
from yyagl.engine.phys import PhysMgr
from yyagl.computer_proxy import ComputerProxy, once_a_frame
from yyagl.racing.weapon.rear_rocket.rear_rocket import RearRocket


ObstInfo = namedtuple('ObstInfo', 'name dist')


class DebugLines(object):

    def __init__(self, color):
        self.color = color
        self.lines = []

    def clear(self):
        map(lambda line: line.remove_node(), self.lines)
        self.lines = []

    def draw(self, start, end, car_name):
        segs = LineSegs()
        segs.set_color(*self.color)
        segs.moveTo(start)
        segs.drawTo(end)
        segs_node = segs.create()
        self.lines += [render.attachNewNode(segs_node)]

    def destroy(self):
        self.clear()


class AbsAiLogic(ComputerProxy):

    def __init__(self, car, cars, show_lines_gnd, show_lines_obst, car_name):
        self.car = car
        self.cars = cars
        self.car_name = car_name
        self.sector2samples_gnd = {'left': [''], 'center': [''], 'right': ['']}
        self.sector2obsts = {'left': [], 'center': [], 'right': []}
        bnds = car.phys.coll_mesh.get_tight_bounds()  # (lowerleft, upperright)
        self.width_bounds = (bnds[0].x * 1.15, bnds[1].x * 1.15)
        whl_height = max(whl.get_wheel_radius() for whl in car.phys.vehicle.get_wheels())
        self.height_bounds = (bnds[0].z - whl_height * 1.15,
                              bnds[1].z + whl_height * 1.15)
        self.debug_lines_gnd = DebugLines((0, 1, 0))
        self.debug_lines_obst = DebugLines((1, 0, 0))
        ComputerProxy.__init__(self)

    @property
    @once_a_frame
    def car_dot_traj(self):
        return self.car.logic.car_vec.dot(self.tgt_vec)

    @property
    @once_a_frame
    def tgt_vec(self):
        return eng.norm_vec(self.curr_tgt_wp.get_pos() - self.car.pos)

    def lookahead_gnd(self, dist, deg):
        lookahed_vec = self.car_vec * dist
        lookahead_rot = eng.rot_vec(lookahed_vec, deg)
        lookahead_pos = self.car.pos + lookahead_rot
        if self.car.fsm.getCurrentOrNextState() != 'Results' and \
                self.car_name == game.player_car.name:
            self.debug_lines_gnd.draw(self.car.pos, lookahead_pos,
                                      self.car_name)
        return self.car.phys.gnd_name(lookahead_pos)

    def _update_gnd(self, direction):  # direction in left, center, right
        if len(self.sector2samples_gnd[direction]) > 0:
            self.sector2samples_gnd[direction].pop(0)
        speed_ratio = self.car.phys.speed_ratio
        center_deg = 10 - 5 * speed_ratio  # central sector's bound to sample into
        lateral_deg = 60 - 55 * speed_ratio
        sector_bounds = {'left': (center_deg, lateral_deg),
                         'center': (-center_deg, center_deg),
                         'right': (-lateral_deg, -center_deg)}
        deg = uniform(*sector_bounds[direction])
        vec_lgt = uniform(9 + 6 * speed_ratio,
                          4 + 29 * speed_ratio)
        self.sector2samples_gnd[direction] += [self.lookahead_gnd(vec_lgt, deg)]

    def get_obstacles(self):
        left_samples = [smp for smp in self.sector2obsts['left'] if smp.dist]
        right_samples = [smp for smp in self.sector2obsts['right'] if smp.dist]
        center_samples = [smp for smp in self.sector2obsts['center'] if smp.dist]
        closest_center = ObstInfo('', 1000)
        closest_left = ObstInfo('', 999)
        closest_right = ObstInfo('', 999)
        if left_samples:
            closest_left = min(left_samples, key=lambda smp: smp.dist)
        if right_samples:
            closest_right = min(right_samples, key=lambda smp: smp.dist)
        if center_samples:
            closest_center = min(center_samples, key=lambda smp: smp.dist)
        return closest_center, closest_left, closest_right

    def clear(self):
        for gnd in ['center', 'left', 'right']:
            for smp in self.sector2obsts[gnd][:]:
                if smp.name == 'Vehicle':
                    self.sector2obsts[gnd].remove(smp)

    def _update_obst(self, gnd):
        if self.car.phys.speed >= 5:
            nsam = 0
        else:
            nsam = 10
        if len(self.sector2obsts[gnd]) > nsam:
            self.sector2obsts[gnd].pop(0)
        lat_deg = 40 - 35 * self.car.phys.speed_ratio
        bounds = {'left': (0, lat_deg), 'center': (0, 0),
                  'right': (-lat_deg, 0)}
        if gnd == 'center':
            offset = (uniform(*self.width_bounds), 0, 0)
        else:
            offset = (self.width_bounds[self.bnd_idx(gnd)], 0, 0)
        start = self.car.gfx.nodepath.get_pos() - self.car_vec * .8
        rot_mat = Mat4()
        rot_mat.setRotateMat(self.car.gfx.nodepath.get_h(), (0, 0, 1))
        offset_rot = rot_mat.xformVec(offset)
        start = start + offset_rot + (0, 0, uniform(*self.height_bounds))
        lgt = 4 + 31 * self.car.phys.speed_ratio
        lookahed_vec = self.car_vec * lgt
        rot_mat = Mat4()
        rot_mat.setRotateMat(uniform(*bounds[gnd]), (0, 0, 1))
        lookahead_rot = rot_mat.xformVec(lookahed_vec)
        lookahead_pos = self.car.gfx.nodepath.get_pos() + lookahead_rot

        b_m = BitMask32.bit(0)
        car_idx = self.cars.index(self.car_name)
        cars_idx = range(len(self.cars))
        cars_idx.remove(car_idx)
        for bitn in cars_idx:
            b_m = b_m | BitMask32.bit(2 + bitn)
        result = PhysMgr().ray_test_closest(start, lookahead_pos, b_m)
        hit = result.get_node()
        dist = 0
        name = ''
        if hit:
            dist = self.car.gfx.nodepath.get_pos() - result.get_hit_pos()
            dist = dist.length()
            name = hit.get_name()
        self.sector2obsts[gnd] += [ObstInfo(name, dist)]
        if self.car.fsm.getCurrentOrNextState() != 'Results' and \
                self.car_name == game.player_car.name:
            self.debug_lines_obst.draw(start, lookahead_pos, self.car_name)

    def destroy(self):
        self.car = None
        self.debug_lines_gnd.destroy()
        self.debug_lines_obst.destroy()
        eng.detach_obs(self.on_start_frame)
        ComputerProxy.destroy(self)


class FrontAiLogic(AbsAiLogic):

    @property
    def curr_tgt_wp(self):  # no need to be cached
        return self.car.logic.closest_wp()[1]

    @property
    def car_vec(self):
        return self.car.logic.car_vec

    @staticmethod
    def bnd_idx(gnd):
        return 0 if gnd == 'left' else 1

    def on_brake(self, distance_center, distance_left, distance_right):
        left = False
        right = False
        min_dist = min([distance_center, distance_left, distance_right])
        if min_dist < 5:
            if self.car.phys.speed < 0:
                if distance_left == min_dist:
                    left = True
                elif distance_right == min_dist:
                    right = True
                return left, right, distance_left < 4, distance_right < 4


class RearAiLogic(AbsAiLogic):

    @property
    def curr_tgt_wp(self):  # no need to be cached
        return self.car.logic.closest_wp()[0]

    @property
    def car_vec(self):
        return -self.car.logic.car_vec

    @staticmethod
    def bnd_idx(gnd):
        return 1 if gnd == 'left' else 0

    def on_brake(self, distance_center, distance_left, distance_right):
        pass


class CarAi(Ai):

    def __init__(self, mdt, car_props, race_props):
        Ai.__init__(self, mdt)
        self.road_name = race_props.road_name
        self.waypoints = car_props.track_waypoints
        self.cars = race_props.cars
        self.front_logic = FrontAiLogic(self.mdt, self.cars, True, True, car_props.name)
        self.rear_logic = RearAiLogic(self.mdt, self.cars, True, True, car_props.name)
        self.positions = []
        self.last_dist_time = 0
        self.last_dist_pos = (0, 0, 0)
        self.last_obst_info = None, 0
        eng.attach_obs(self.on_frame)

    def __eval_gnd(self):
        has_pos_speed = self.mdt.phys.speed >= 0
        curr_logic = self.front_logic if has_pos_speed else self.rear_logic
        road_n = self.road_name

        def n_road(samples):
            return len([smp for smp in samples if smp.startswith(road_n)])
        r_road = lambda samples: float(n_road(samples)) / len(samples)
        r_left = r_road(curr_logic.sector2samples_gnd['left'])
        r_center = r_road(curr_logic.sector2samples_gnd['center'])
        r_right = r_road(curr_logic.sector2samples_gnd['right'])
        r_max = max([r_left, r_center, r_right])
        # if self.mdt.name == game.player_car.name:
        #     print curr_logic.sector2samples_gnd
        if r_left < .3 and r_right > .6:
            return 'right'
        elif r_right < .3 and r_left > .6:
            return 'left'
        else:
            if r_center == r_max:
                return 'center'
            elif r_left == r_max:
                return 'left'
            else:
                return 'right'

    def on_frame(self):
        self._update_dist()
        if hasattr(self.front_logic, 'debug_lines_gnd'):
            self.front_logic.debug_lines_gnd.clear()
        if hasattr(self.front_logic, 'debug_lines_obst'):
            self.front_logic.debug_lines_obst.clear()
        if hasattr(self.rear_logic, 'debug_lines_gnd'):
            self.rear_logic.debug_lines_gnd.clear()
        if hasattr(self.rear_logic, 'debug_lines_obst'):
            self.rear_logic.debug_lines_obst.clear()
        self.front_logic._update_gnd('center')
        self.front_logic._update_gnd('left')
        self.front_logic._update_gnd('right')
        self.front_logic.clear()
        self.front_logic._update_obst('center')
        self.front_logic._update_obst('left')
        self.front_logic._update_obst('right')
        if self.mdt.phys.speed < 10 or self.mdt.logic.weapon and self.mdt.logic.weapon.__class__ == RearRocket:
            self.rear_logic._update_gnd('center')
            self.rear_logic._update_gnd('left')
            self.rear_logic._update_gnd('right')
            self.rear_logic._update_obst('center')
            self.rear_logic._update_obst('left')
            self.rear_logic._update_obst('right')

    def _update_dist(self):
        if self.mdt.fsm.getCurrentOrNextState() in ['Loading', 'Countdown']:
            return
        curr_time = globalClock.getFrameTime()
        if curr_time - self.last_dist_time < 1:
            return
        self.last_dist_time = curr_time
        self.positions += [self.mdt.gfx.nodepath.get_pos()]
        if len(self.positions) > 12:
            self.positions.pop(0)
        else:
            return
        npos = len(self.positions)
        center_x = sum(pos.get_x() for pos in self.positions) / npos
        center_y = sum(pos.get_y() for pos in self.positions) / npos
        center_z = sum(pos.get_z() for pos in self.positions) / npos
        center = LPoint3f(center_x, center_y, center_z)
        if all((pos - center).length() < 6 for pos in self.positions):
            self.positions = []
            self.mdt.event.process_respawn()

    def brake(self, obstacles, obstacles_back):
        has_pos_speed = self.mdt.phys.speed >= 0
        curr_logic = self.front_logic if has_pos_speed else self.rear_logic
        closest_center, closest_left, closest_right = obstacles
        closest_center_b, closest_left_b, closest_right_b = obstacles_back
        dist_c = 4 if closest_center.name == 'Vehicle' else 8
        dist_l = 4 if closest_left.name == 'Vehicle' else 8
        dist_r = 4 if closest_right.name == 'Vehicle' else 8
        if self.mdt.phys.speed < 0:
            d_c = closest_center.dist < dist_c
            d_l = closest_left.dist < dist_l
            d_r = closest_right.dist < dist_r
            if (d_c or d_l or d_r) and closest_center_b.dist > 2:
                return True
        else:
            dist = 1 if closest_center.name == 'Vehicle' else 5
            dist_c = 3 + dist * self.mdt.phys.speed_ratio
            if closest_center.dist < dist_c and closest_center_b.dist > 2:
                return True
        if self.mdt.phys.speed < 40:
            return False
        return curr_logic.car_dot_traj < .4

    @property
    def is_on_road(self):
        grounds = self.mdt.phys.gnd_names
        return all(name.startswith(self.road_name) for name in grounds)

    @property
    def acceleration(self):
        has_pos_speed = self.mdt.phys.speed >= 0
        curr_logic = self.front_logic if has_pos_speed else self.rear_logic
        if self.mdt.phys.speed < 40:
            return True
        if not self.is_on_road:
            return False
        return curr_logic.car_dot_traj > .8

    def left_right(self, obstacles, brake, obstacles_back):
        curr_time = globalClock.getFrameTime()
        if curr_time - self.last_obst_info[1] < .05:
            return self.last_obst_info[0]

        if brake and self.mdt.phys.speed < 10:
            closest_center, closest_left, closest_right = obstacles_back
        else:
            closest_center, closest_left, closest_right = obstacles

        has_pos_speed = self.mdt.phys.speed >= 0
        curr_logic = self.front_logic if has_pos_speed else self.rear_logic
        dist_far = 4 + self.mdt.phys.speed_ratio * 8
        dist_close = 2 + self.mdt.phys.speed_ratio * 2
        if brake and self.mdt.phys.speed < 10:
            dist_far = 12
            dist_close = 4
        obst_center = closest_center.dist < dist_far
        obst_left = closest_left.dist < dist_far
        obst_right = closest_right.dist < dist_far
        has_obst_center = closest_center.dist < dist_close
        has_obst_left = closest_left.dist < dist_close
        has_obst_right = closest_right.dist < dist_close
        obst_center_back = closest_center.dist < dist_far
        obst_left_back = closest_left.dist < dist_far
        obst_right_back = closest_right.dist < dist_far
        has_obst_center_back = closest_center.dist < dist_close
        has_obst_left_back = closest_left.dist < dist_close
        has_obst_right_back = closest_right.dist < dist_close
        car_vec = self.mdt.logic.car_vec
        tgt = Vec3(curr_logic.tgt_vec.x, curr_logic.tgt_vec.y, 0)
        dot_res = tgt.cross(Vec3(car_vec.x, car_vec.y, 0)).dot(Vec3(0, 0, 1))

        # eval backward
        if curr_logic.car_dot_traj < -.2:
            left, right = dot_res < 0, dot_res >= 0
            if brake and self.mdt.phys.speed < 10:
                left = left and not has_obst_left_back
                right = right and not has_obst_right_back
                if left or right:
                    return left, right
            else:
                if not brake:
                    left = left and not has_obst_left
                    right = right and not has_obst_right
                    if left or right:
                        return left, right

        # eval obstacles
        if brake and self.mdt.phys.speed < 10:
            curr_obs_center = obst_center_back
            curr_obs_left = obst_left_back
            curr_obs_right = obst_right_back
            curr_has_obs_left = has_obst_left_back
            curr_has_obs_right = has_obst_right_back
        else:
            curr_obs_center = obst_center
            curr_obs_left = obst_left
            curr_obs_right = obst_right
            curr_has_obs_left = has_obst_left
            curr_has_obs_right = has_obst_right
        if curr_obs_left or curr_obs_right or curr_obs_center:
            if brake and self.mdt.phys.speed < 10:
                left, right = False, False
                if curr_obs_center:
                    left, right = not curr_obs_right, not curr_obs_left
                    if left and right:
                        max_d = max([closest_center.dist, closest_left.dist,
                                     closest_right.dist])
                        if max_d == closest_center.dist:
                            left, right = False, False
                        elif max_d == closest_left.dist:
                            left, right = False, True
                        else:
                            left, right = True, False
            else:
                left, right = False, False
                if curr_obs_center:
                    left, right = not curr_obs_left, not curr_obs_right
                    if left and right:
                        max_d = max([closest_center.dist, closest_left.dist,
                                     closest_right.dist])
                        if max_d == closest_center.dist:
                            left, right = False, False
                        elif max_d == closest_left.dist:
                            left, right = True, False
                        else:
                            left, right = False, True
            if left or right:
                self.last_obst_info = (left, right), curr_time
                return left, right

        # eval on_road
        gnd_dir = self.__eval_gnd()
        # if curr_logic.car_dot_traj > 0 and gnd_dir != 'center':
        if gnd_dir == 'left':
            if brake and self.mdt.phys.speed < 10 and not curr_has_obs_left:
                return False, True
            elif brake and self.mdt.phys.speed < 10 and not curr_has_obs_right:
                return True, False
            elif not brake and not curr_has_obs_left:
                return True, False
            elif not brake and not curr_has_obs_right:
                return False, True
        elif gnd_dir == 'right':
            if brake and self.mdt.phys.speed < 10 and not curr_has_obs_left:
                return True, False
            elif brake and self.mdt.phys.speed < 10 and not curr_has_obs_right:
                return False, True
            elif not brake and not curr_has_obs_left:
                return False, True
            elif not brake and not curr_has_obs_right:
                return True, False

        # eval waypoints
        # if self.mdt.name == game.player_car.name:
        #     print 'dot', curr_logic.car_dot_traj
        if abs(curr_logic.car_dot_traj) > .98:
            return False, False
        car_vec = curr_logic.car_vec
        tgt = Vec3(curr_logic.tgt_vec.x, curr_logic.tgt_vec.y, 0)
        dot_res = tgt.cross(Vec3(car_vec.x, car_vec.y, 0)).dot(Vec3(0, 0, 1))
        if brake and self.mdt.phys.speed < 10:
            left, right = dot_res >= 0, dot_res < 0
        else:
            left, right = dot_res < 0, dot_res >= 0
        if brake and self.mdt.phys.speed < 10:
            if left:
                if curr_has_obs_right:
                    left = False
            if right:
                if curr_has_obs_left:
                    right = False
        elif not brake:
            if left:
                if curr_has_obs_left:
                    left = False
            if right:
                if curr_has_obs_right:
                    right = False
        return left, right

    def get_input(self):
        # import time; time.sleep(.01)
        # if self.mdt.name == game.player_car.name:
        #     print 'dot_prod', self.car_dot_traj
        # if self.mdt.name == game.player_car.name:
        #     print 'speed', self.mdt.phys.speed
        obstacles = list(self.front_logic.get_obstacles())
        # if self.mdt.name == game.player_car.name:
        #     print 'obstacles', obstacles
        obstacles_back = list(self.rear_logic.get_obstacles())
        # if self.mdt.name == game.player_car.name:
        #     print 'obstacles_back', obstacles_back
        brake = self.brake(obstacles, obstacles_back)
        # if self.mdt.name == game.player_car.name:
        #    print 'brake', brake
        acceleration = False if brake else self.acceleration
        # if self.mdt.name == game.player_car.name:
        #     print 'acceleration', acceleration
        left, right = self.left_right(obstacles, brake, obstacles_back)
        # if self.mdt.name == game.player_car.name:
        #     print 'left, right', left, right
        # if self.mdt.name == game.player_car.name:
        #     print self.__eval_gnd()
        # if self.mdt.name == game.player_car.name:
        #     print left, right, brake, acceleration, self.__eval_gnd(), \
        #         self.front_logic.car_dot_traj, self.mdt.phys.speed, \
        #         obstacles, obstacles_back
        if self.mdt.logic.weapon:
            if self.mdt.logic.weapon.ai_fire():
                self.mdt.logic.fire()
        return {'forward': acceleration, 'left': left, 'reverse': brake,
                'right': right}

    def destroy(self):
        eng.detach_obs(self.on_frame)
        self.front_logic.destroy()
        self.rear_logic.destroy()
        Ai.destroy(self)


class CarResultsAi(CarAi):

    def _end_async(self):
        pass
