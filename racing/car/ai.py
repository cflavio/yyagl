from random import uniform
from panda3d.core import Vec3, Vec2, Point3, Mat4, BitMask32, LineSegs, LPoint3f
from yyagl.gameobject import Ai


class DebugLines(object):

    def __init__(self, car, color):
        self.car = car
        self.color = color

    def draw(self, start, end):
        if self.car.fsm.getCurrentOrNextState() != 'Results':
            if hasattr(self, 'gnd_lines'):
                self.gnd_lines.remove_node()
            if self.car.name == game.player_car.name:
                segs = LineSegs()
                segs.set_color(*self.color)
                segs.moveTo(start)
                segs.drawTo(end)
                segs_node = segs.create()
                self.gnd_lines = render.attachNewNode(segs_node)

    def destroy(self):
        self.car = None


class AbsAiLogic(object):

    def __init__(self, car, cars):
        self.car = car
        self.cars = cars
        self.curr_gnd = 'left'
        self.gnd_samples = {'left': [''], 'center': [''],  'right': ['']}
        self.obst_samples = {'left': [], 'center': [],  'right': []}
        bnds = car.phys.coll_mesh.get_tight_bounds()
        self.width_bounds = (bnds[0][0] * 1.15, bnds[1][0] * 1.15)
        self.height_bounds = (bnds[0][2] - .4, bnds[1][2] + .4)  # wheel's height
        self.debug_lines_gnd = DebugLines(self.car, (0, 1, 0))
        self.debug_lines_obst = DebugLines(self.car, (1, 0, 0))

    @property
    def curr_dot_prod(self):  # to be cached
        return self.car.logic.car_vec.dot(self.tgt_vec)

    @property
    def tgt_vec(self):  # to be cached
        #if self.car.name == game.player_car.name: print 'tgt', self.current_target
        curr_tgt_pos = self.current_target.get_pos()
        curr_pos = self.car.gfx.nodepath.get_pos()
        tgt_vec = Vec3(curr_tgt_pos - curr_pos)
        tgt_vec.normalize()
        return tgt_vec

    def lookahead_ground(self, dist, deg):
        lookahed_vec = self.car_vec * dist
        rot_mat = Mat4()
        rot_mat.setRotateMat(deg, (0, 0, 1))
        lookahead_rot = rot_mat.xformVec(lookahed_vec)
        lookahead_pos = self.car.gfx.nodepath.get_pos() + lookahead_rot
        self.debug_lines_gnd.draw(self.car.gfx.nodepath.get_pos(), lookahead_pos)
        return self.car.phys.gnd_name(lookahead_pos)

    def _update_gnd(self):
        if len(self.gnd_samples[self.curr_gnd]) > 0:
            self.gnd_samples[self.curr_gnd].pop(0)
        center_deg = 10 - 5 * self.car.phys.speed_ratio
        lateral_deg = 45 - 40 * self.car.phys.speed_ratio
        bounds = {'left': (center_deg, lateral_deg), 'center': (-center_deg, center_deg), 'right': (-lateral_deg, -center_deg)}
        deg = uniform(*bounds[self.curr_gnd])
        lgt = uniform(4 + 11 * self.car.phys.speed_ratio, 4 + 29 * self.car.phys.speed_ratio)
        self.gnd_samples[self.curr_gnd] += [self.lookahead_ground(lgt, deg)]
        dirs = ['left', 'center', 'right']
        self.curr_gnd = dirs[(dirs.index(self.curr_gnd) + 1) % len(dirs)]

    def _get_obstacles(self):
        left_samples = [smp for smp in self.obst_samples['left'] if smp[1]]
        right_samples = [smp for smp in self.obst_samples['right'] if smp[1]]
        center_samples = [smp for smp in self.obst_samples['center'] if smp[1]]
        min_center = '', 1000
        min_left = '', 999
        min_right = '', 999
        if left_samples:
            min_left = min(left_samples, key=lambda elm: elm[1])
        if right_samples:
            min_right = min(right_samples, key=lambda elm: elm[1])
        if center_samples:
            min_center = min(center_samples, key=lambda elm: elm[1])
        return min_center[0], min_center[1], min_left[0], min_left[1], min_right[0], min_right[1]

    def _update_obst(self):
        nsam = 4 if self.curr_gnd == 'center' else 1
        if len(self.obst_samples[self.curr_gnd]) > nsam:
            self.obst_samples[self.curr_gnd].pop(0)
        lat_deg = 40 - 35 * self.car.phys.speed_ratio
        bounds = {'left': (0, lat_deg), 'center': (0, 0), 'right': (-lat_deg, 0)}
        if self.curr_gnd == 'center':
            offset = (uniform(*self.width_bounds), 0, 0)
            deg = 0
        else:
            offset = (self.width_bounds[self.bnd_idx()], 0, 0)
            deg = uniform(*bounds[self.curr_gnd])
        start = self.car.gfx.nodepath.get_pos() - self.car_vec * .8
        rot_mat = Mat4()
        rot_mat.setRotateMat(self.car.gfx.nodepath.get_h(), (0, 0, 1))
        offset_rot = rot_mat.xformVec(offset)
        start = start + offset_rot + (0, 0, uniform(*self.height_bounds))
        lgt = 4 + 31 * self.car.phys.speed_ratio
        lookahed_vec = self.car_vec * lgt
        rot_mat = Mat4()
        rot_mat.setRotateMat(uniform(*bounds[self.curr_gnd]), (0, 0, 1))
        lookahead_rot = rot_mat.xformVec(lookahed_vec)
        lookahead_pos = self.car.gfx.nodepath.get_pos() + lookahead_rot

        b_m = BitMask32.bit(0)
        car_idx = self.cars.index(self.car.name)
        cars_idx = range(len(self.cars))
        cars_idx.remove(car_idx)
        for bitn in cars_idx:
            b_m = b_m | BitMask32.bit(2 + bitn)
        result = eng.ray_test_closest(start, lookahead_pos, b_m)
        hit = result.get_node()
        dist = 0
        name = ''
        if hit:
            dist = self.car.gfx.nodepath.get_pos() - result.get_hit_pos()
            dist = dist.length()
            name = hit.get_name()
        self.obst_samples[self.curr_gnd] += [(name, dist)]
        self.debug_lines_obst.draw(start, lookahead_pos)

    def _eval_obstacle_avoidance(self, obstacles, brake):
        name_c, distance_center, name_l, distance_left, name_r, distance_right = obstacles
        left = False
        right = False
        if brake:
            ret = self.on_brake(distance_center, distance_left, distance_right)
            if ret:
                return ret
        if distance_left == max([distance_center, distance_left, distance_right]):
            left = True
        elif distance_right == max([distance_center, distance_left, distance_right]):
            right = True
        return left, right, distance_left < 4, distance_right < 4

    def destroy(self):
        self.car = None
        self.debug_lines_gnd.destroy()
        self.debug_lines_obst.destroy()


class FrontAiLogic(AbsAiLogic):

    @property
    def current_target(self):  # no need to be cached
        return self.car.logic.closest_wp()[1]

    @property
    def car_vec(self):
        return self.car.logic.car_vec

    def bnd_idx(self):
        return 0 if self.curr_gnd == 'left' else 1

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
    def current_target(self):  # no need to be cached
        return self.car.logic.closest_wp()[0]

    @property
    def car_vec(self):
        return -self.car.logic.car_vec

    def bnd_idx(self):
        return 1 if self.curr_gnd == 'left' else 0

    def on_brake(self, distance_center, distance_left, distance_right):
        pass


class CarAi(Ai):

    def __init__(self, mdt, road_name, waypoints, cars):
        Ai.__init__(self, mdt)
        self.road_name = road_name
        self.waypoints = waypoints
        self.cars = cars
        self.front_logic = FrontAiLogic(self.mdt, self.cars)
        self.rear_logic = RearAiLogic(self.mdt, self.cars)
        self.positions = []
        self.last_dist_time = 0
        self.last_dist_pos = (0, 0, 0)
        self.last_obst_info = None, 0
        eng.attach_obs(self.on_frame)

    def __eval_gnd(self):
        curr_logic = self.front_logic if self.mdt.phys.speed >= 0 else self.rear_logic
        road_n = self.road_name
        n_road = lambda samples: len([smp for smp in samples if smp.startswith(road_n)])
        r_road = lambda samples: float(n_road(samples)) / len(samples)
        r_left = r_road(curr_logic.gnd_samples['left'])
        r_center = r_road(curr_logic.gnd_samples['center'])
        r_right = r_road(curr_logic.gnd_samples['right'])
        r_max = max([r_left, r_center, r_right])
        if self.mdt.name == game.player_car.name: print 'road factors:', curr_logic.gnd_samples
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
        self.front_logic._update_gnd()
        self.front_logic._update_obst()
        if self.mdt.phys.speed < 10:
            self.rear_logic._update_gnd()
            self.rear_logic._update_obst()

    def _update_dist(self):
        if self.mdt.fsm.getCurrentOrNextState() in ['Loading', 'Countdown']:
            return
        curr_time = globalClock.getFrameTime()
        if curr_time - self.last_dist_time < 1:
            return
        self.last_dist_time = curr_time
        self.positions += [self.mdt.gfx.nodepath.get_pos()]
        if len(self.positions) > 10:
            self.positions.pop(0)
        else:
            return
        center_x = sum(pos.get_x() for pos in self.positions) / len(self.positions)
        center_y = sum(pos.get_y() for pos in self.positions) / len(self.positions)
        center_z = sum(pos.get_z() for pos in self.positions) / len(self.positions)
        center = LPoint3f(center_x, center_y, center_z)
        if all((pos - center).length() < 6 for pos in self.positions):
            self.positions = []
            self.mdt.event.process_respawn()

    def brake(self, obstacles):
        curr_logic = self.front_logic if self.mdt.phys.speed >= 0 else self.rear_logic
        name_c, distance_center, name_l, distance_left, name_r, distance_right = obstacles
        if distance_center < 5:
            return True
        if self.mdt.phys.speed < 40:
            return False
        return curr_logic.curr_dot_prod < .4

    @property
    def acceleration(self):
        curr_logic = self.front_logic if self.mdt.phys.speed >= 0 else self.rear_logic
        if self.mdt.phys.speed < 40:
            return True
        grounds = self.mdt.phys.gnd_names
        if not all(name.startswith(self.road_name) for name in grounds):
            return False
        return curr_logic.curr_dot_prod > .8

    def left_right(self, obstacles, brake, obstacles_back):
        curr_time = globalClock.getFrameTime()
        if curr_time - self.last_obst_info[1] < .05:
            return self.last_obst_info[0]

        curr_logic = self.front_logic if self.mdt.phys.speed >= 0 else self.rear_logic
        obst_left, obst_right, has_obst_left, has_obst_right = self.front_logic._eval_obstacle_avoidance(obstacles, brake)
        obst_left_back, obst_right_back, has_obst_left_back, has_obst_right_back = self.rear_logic._eval_obstacle_avoidance(obstacles_back, brake)
        car_vec = self.mdt.logic.car_vec
        tgt = Vec3(curr_logic.tgt_vec.x, curr_logic.tgt_vec.y, 0)
        dot_res = tgt.cross(Vec3(car_vec.x, car_vec.y, 0)).dot(Vec3(0, 0, 1))

        # eval backward
        if curr_logic.curr_dot_prod < -.2:
            left, right = dot_res < 0, dot_res >= 0
            if brake and self.mdt.phys.speed < 0:
                left, right = left and not has_obst_left_back, right and not has_obst_right_back
                if left or right:
                    return left, right
            else:
                if self.mdt.phys.speed > 0:
                    left, right = left and not has_obst_left, right and not has_obst_right
                    if left or right:
                        return left, right

        # eval obstacles
        if brake and self.mdt.phys.speed < 0:
            curr_obs_left = obst_left_back
            curr_obs_right = obst_right_back
        else:
            curr_obs_left = obst_left
            curr_obs_right = obst_right
        if curr_obs_left or curr_obs_right:
            if abs(curr_obs_left - curr_obs_right) < 4:
                close_left, close_right = dot_res < 0, dot_res >= 0
            else:
                close_left, close_right = curr_obs_left, curr_obs_right
            self.last_obst_info = (close_left, close_right), curr_time
            return close_left, close_right

        # eval on_road
        road_n = self.road_name
        gnd_dir = self.__eval_gnd()
        if curr_logic.curr_dot_prod > 0 and gnd_dir != 'center':
            if gnd_dir == 'left':
                return True, False
            elif gnd_dir == 'right':
                return False, True

        # eval waypoints
        #if self.mdt.name == game.player_car.name: print 'dot', curr_logic.curr_dot_prod
        if abs(curr_logic.curr_dot_prod) > .98:
            return False, False
        car_vec = self.mdt.logic.car_vec
        tgt = Vec3(curr_logic.tgt_vec.x, curr_logic.tgt_vec.y, 0)
        dot_res = tgt.cross(Vec3(car_vec.x, car_vec.y, 0)).dot(Vec3(0, 0, 1))
        return dot_res < 0, dot_res >= 0

    def get_input(self):
        #import time; time.sleep(.01)
        #if self.mdt.name == game.player_car.name: print 'dot_prod', self.curr_dot_prod
        #if self.mdt.name == game.player_car.name: print 'speed', self.mdt.phys.speed
        obstacles = list(self.front_logic._get_obstacles())
        #if self.mdt.name == game.player_car.name: print 'obstacles', obstacles
        obstacles_back = list(self.rear_logic._get_obstacles())
        #if self.mdt.name == game.player_car.name: print 'obstacles_back', obstacles_back
        brake = self.brake(obstacles)
        #if self.mdt.name == game.player_car.name: print 'brake', brake
        acceleration = False if brake else self.acceleration
        #if self.mdt.name == game.player_car.name: print 'acceleration', acceleration
        left, right = self.left_right(obstacles, brake, obstacles_back)
        #if self.mdt.name == game.player_car.name: print 'left, right', left, right
        #if self.mdt.name == game.player_car.name: print self.__eval_gnd()
        if self.mdt.name == game.player_car.name: print left, right, self.__eval_gnd(), self.front_logic.curr_dot_prod, obstacles, obstacles_back
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
