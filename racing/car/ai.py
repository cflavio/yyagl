from panda3d.core import Vec3, Vec2, Point3, Mat4, BitMask32, LineSegs
from yyagl.gameobject import Ai


class CarAi(Ai):

    def __init__(self, mdt, road_name, waypoints):
        Ai.__init__(self, mdt)
        self.road_name = road_name
        self.waypoints = waypoints

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
        min_dist = min([distance_center, distance_left, distance_right])
        if min_dist < 4:
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
        start = self.mdt.gfx.nodepath.get_pos() - self.mdt.logic.car_vec * 1
        lookahed_vec = self.mdt.logic.car_vec * 25
        end = start + lookahed_vec
        result = eng.ray_test_closest(start, end, BitMask32.bit(0))
        hit = result.get_node()
        lookahed_vec = self.mdt.logic.car_vec * 25
        left_rot_mat = Mat4()
        left_rot_mat.setRotateMat(12, (0, 0, 1))
        lookahead_rot_left = left_rot_mat.xformVec(lookahed_vec)
        lookahead_pos_left = self.mdt.gfx.nodepath.get_pos() + lookahead_rot_left
        lookahed_vec = self.mdt.logic.car_vec * 25
        right_rot_mat = Mat4()
        right_rot_mat.setRotateMat(-12, (0, 0, 1))
        lookahead_rot_right = right_rot_mat.xformVec(lookahed_vec)
        lookahead_pos_right = self.mdt.gfx.nodepath.get_pos() + lookahead_rot_right
        #print end, lookahead_pos_left, lookahead_pos_right
        result_left = eng.ray_test_closest(start, lookahead_pos_left, BitMask32.bit(0))
        hit_left = result_left.get_node()
        result_right = eng.ray_test_closest(start, lookahead_pos_right, BitMask32.bit(0))
        hit_right = result_left.get_node()
        distance_left = 999
        if hit_left:
            dist_vec = self.mdt.gfx.nodepath.get_pos() - result_left.get_hit_pos()
            distance_left = dist_vec.length()
        distance_right = 999
        if hit_right:
            dist_vec = self.mdt.gfx.nodepath.get_pos() - result_right.get_hit_pos()
            distance_right = dist_vec.length()
        distance_center = 1000
        if hit:
            dist_vec = self.mdt.gfx.nodepath.get_pos() - result.get_hit_pos()
            distance_center = dist_vec.length()
        distance_center = min(1000, distance_center)
        distance_left = min(999, distance_left)
        distance_right = min(999, distance_right)
        name_c = name_l = name_r = ''
        if hit:
            name_c = hit.get_name()
        if hit_left:
            name_l = hit_left.get_name()
        if hit_right:
            name_r = hit_right.get_name()
        if self.mdt.fsm.getCurrentOrNextState() != 'Results':
            if hasattr(self, 'ai_lines'):
                self.ai_lines.remove_node()
            if self.mdt.name == game.player_car.name:
                segs = LineSegs()
                segs.moveTo(start)
                segs.drawTo(end)
                segs.moveTo(start)
                segs.drawTo(lookahead_pos_left)
                segs.moveTo(start)
                segs.drawTo(lookahead_pos_right)
                segs_node = segs.create()
                self.ai_lines = render.attachNewNode(segs_node)
        return name_c, distance_center, name_l, distance_left, name_r, distance_right

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
                    #if self.mdt.name == game.player_car.name:
                    #    print name_c, distance_center, name_l, distance_left, name_r, distance_right, left, right
                    return left, right
        if distance_left == max([distance_center, distance_left, distance_right]):
            left = True
        elif distance_right == max([distance_center, distance_left, distance_right]):
            right = True
        #if self.mdt.name == game.player_car.name:
        #    print name_c, distance_center, name_l, distance_left, name_r, distance_right, left, right
        return left, right

    def left_right(self, obstacles, brake):
        obst_left, obst_right = self.__eval_obstacle_avoidance(obstacles, brake)
        if obst_left or obst_right:
            return obst_left, obst_right
        road_n = self.road_name
        fwd_gnd = self.lookahead_ground(30, 0)
        right_gnd = self.lookahead_ground(30, -20)
        left_gnd = self.lookahead_ground(30, 20)
        fwd_gnd_close = self.lookahead_ground(10, 0)
        right_gnd_close = self.lookahead_ground(10, -30)
        left_gnd_close = self.lookahead_ground(10, 30)
        if self.curr_dot_prod > 0 and not fwd_gnd.startswith(road_n):
            if left_gnd.startswith(road_n):
                return True, False
            elif right_gnd.startswith(road_n):
                return False, True
        if self.curr_dot_prod > 0 and not fwd_gnd_close.startswith(road_n):
            if left_gnd_close.startswith(road_n):
                return True, False
            elif right_gnd_close.startswith(road_n):
                return False, True
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


class CarResultsAi(CarAi):

    def _end_async(self):
        pass
