from random import uniform
from panda3d.core import Vec3, Vec2, Point3, Mat4, BitMask32, LineSegs
from yyagl.gameobject import Ai


class CarAi(Ai):

    def __init__(self, mdt, road_name, waypoints):
        Ai.__init__(self, mdt)
        self.road_name = road_name
        self.waypoints = waypoints
        self.gnd_samples = {'left': [''], 'center': [''],  'right': ['']}
        self.obst_samples = {'left': [], 'center': [],  'right': []}
        self.curr_gnd = 'left'
        self.last_obst_info = None, 0
        bnds = self.mdt.phys.coll_mesh.get_tight_bounds()
        self.width_bounds = (bnds[0][0], bnds[1][0])
        eng.attach_obs(self.on_frame)

    @property
    def current_target(self):  # no need to be cached
        curr_wp = self.mdt.logic.closest_wp()[1]
        wpn = len(self.waypoints)
        next_wp_idx = (self.waypoints.keys().index(curr_wp) + 1) % wpn
        dist_vec = curr_wp.get_pos() - self.mdt.gfx.nodepath.get_pos()
        distance = dist_vec.length()
        return curr_wp if distance > 15 else self.waypoints.keys()[next_wp_idx]

    @property
    def tgt_vec(self):  # to be cached
        curr_tgt_pos = self.current_target.get_pos()
        curr_pos = self.mdt.gfx.nodepath.get_pos()
        tgt_vec = Vec3(curr_tgt_pos - curr_pos)
        tgt_vec.normalize()
        return tgt_vec

    @property
    def curr_dot_prod(self):  # to be cached
        return self.mdt.logic.car_vec.dot(self.tgt_vec)

    def brake(self, obstacles):
        name_c, distance_center, name_l, distance_left, name_r, distance_right = obstacles
        if distance_center < 4:
            return True
        if self.mdt.phys.speed < 40:
            return False
        return self.curr_dot_prod < .4

    @property
    def acceleration(self):
        if self.mdt.phys.speed < 40:
            return True
        grounds = self.mdt.phys.gnd_names
        if not all(name.startswith(self.road_name) for name in grounds):
            return False
        return self.curr_dot_prod > .8

    def lookahead_ground(self, dist, deg):
        lookahed_vec = self.mdt.logic.car_vec * dist
        rot_mat = Mat4()
        rot_mat.setRotateMat(deg, (0, 0, 1))
        lookahead_rot = rot_mat.xformVec(lookahed_vec)
        lookahead_pos = self.mdt.gfx.nodepath.get_pos() + lookahead_rot
        return self.mdt.phys.gnd_name(lookahead_pos)

    def __get_obstacles(self):
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

    def __eval_obstacle_avoidance(self, obstacles, brake):
        name_c, distance_center, name_l, distance_left, name_r, distance_right = obstacles
        left = False
        right = False
        if brake:
            min_dist = min([distance_center, distance_left, distance_right])
            if min_dist < 5:
                if self.mdt.phys.speed < 0:
                    if distance_left == min_dist:
                        left = True
                    elif distance_right == min_dist:
                        right = True
                    return left, right
        if distance_left == max([distance_center, distance_left, distance_right]):
            left = True
        elif distance_right == max([distance_center, distance_left, distance_right]):
            right = True
        return left, right

    def __update_gnd(self):
        if len(self.gnd_samples[self.curr_gnd]) > 5:
            self.gnd_samples[self.curr_gnd].pop(0)
        bounds = {'left': (10, 30), 'center': (-10, 10), 'right': (-30, -10)}
        deg = uniform(*bounds[self.curr_gnd])
        lgt = uniform(5, 25)
        self.gnd_samples[self.curr_gnd] += [self.lookahead_ground(deg, lgt)]
        dirs = ['left', 'center', 'right']
        self.curr_gnd = dirs[(dirs.index(self.curr_gnd) + 1) % len(dirs)]

    def __eval_gnd(self):
        road_n = self.road_name
        n_road = lambda samples: len([smp for smp in samples if smp.startswith(road_n)])
        r_road = lambda samples: float(n_road(samples)) / len(samples)
        r_left = r_road(self.gnd_samples['left'])
        r_center = r_road(self.gnd_samples['center'])
        r_right = r_road(self.gnd_samples['right'])
        r_max = max([r_left, r_center, r_right])
        if r_center == r_max:
            return 'center'
        elif r_left == r_max:
            return 'left'
        else:
            return 'right'

    def __update_obst(self):
        if len(self.obst_samples[self.curr_gnd]) > 5:
            self.obst_samples[self.curr_gnd].pop(0)
        bounds = {'left': (0, 25), 'center': (0, 0), 'right': (-25, 0)}
        if self.curr_gnd == 'center':
            offset = (uniform(*self.width_bounds), 0, 0)
            deg = 0
        else:
            offset = (self.width_bounds[0 if self.curr_gnd == 'left' else 1], 0, 0)
            deg = uniform(*bounds[self.curr_gnd])
        start = self.mdt.gfx.nodepath.get_pos() - self.mdt.logic.car_vec * 1
        rot_mat = Mat4()
        rot_mat.setRotateMat(self.mdt.gfx.nodepath.get_h(), (0, 0, 1))
        offset_rot = rot_mat.xformVec(offset)
        start = start + offset_rot
        lgt = 5 + 20 * self.mdt.phys.speed_ratio
        lookahed_vec = self.mdt.logic.car_vec * lgt
        rot_mat = Mat4()
        rot_mat.setRotateMat(uniform(*bounds[self.curr_gnd]), (0, 0, 1))
        lookahead_rot = rot_mat.xformVec(lookahed_vec)
        lookahead_pos = self.mdt.gfx.nodepath.get_pos() + lookahead_rot
        result = eng.ray_test_closest(start, lookahead_pos, BitMask32.bit(0))
        hit = result.get_node()
        dist = 0
        name = ''
        if hit:
            dist = self.mdt.gfx.nodepath.get_pos() - result.get_hit_pos()
            dist = dist.length()
            name = hit.get_name()
        self.obst_samples[self.curr_gnd] += [(name, dist)]
        if self.mdt.fsm.getCurrentOrNextState() != 'Results':
            if hasattr(self, 'ai_lines'):
                self.ai_lines.remove_node()
            if self.mdt.name == game.player_car.name:
                segs = LineSegs()
                segs.moveTo(start)
                segs.drawTo(lookahead_pos)
                segs_node = segs.create()
                self.ai_lines = render.attachNewNode(segs_node)

    def on_frame(self):
        self.__update_gnd()
        self.__update_obst()

    def left_right(self, obstacles, brake):
        # eval obstacles
        curr_time = globalClock.getFrameTime()
        if curr_time - self.last_obst_info[1] < .1:
            return self.last_obst_info[0]
        obst_left, obst_right = self.__eval_obstacle_avoidance(obstacles, brake)
        if obst_left or obst_right:
            self.last_obst_info = (obst_left, obst_right), curr_time
            return obst_left, obst_right

        # eval on_road
        road_n = self.road_name
        gnd_dir = self.__eval_gnd()
        if self.curr_dot_prod > 0 and gnd_dir != 'center':
            if gnd_dir == 'left':
                return True, False
            elif gnd_dir == 'right':
                return False, True

        # eval waypoints
        if abs(self.curr_dot_prod) > .9:
            return False, False
        car_vec = self.mdt.logic.car_vec
        tgt = Vec3(self.tgt_vec.x, self.tgt_vec.y, 0)
        dot_res = tgt.cross(Vec3(car_vec.x, car_vec.y, 0)).dot(Vec3(0, 0, 1))
        return dot_res < 0, dot_res >= 0

    def get_input(self):
        obstacles = list(self.__get_obstacles())
        brake = self.brake(obstacles)
        acceleration = False if brake else self.acceleration
        left, right = self.left_right(obstacles, brake)
        return {'forward': acceleration, 'left': left, 'reverse': brake,
                'right': right}

    def destroy(self):
        eng.detach_obs(self.on_frame)
        Ai.destroy(self)

class CarResultsAi(CarAi):

    def _end_async(self):
        pass
