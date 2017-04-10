from panda3d.core import Vec3, Vec2, Point3, Mat4
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

    @property
    def brake(self):
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
        lookahead_pos = self.mdt.gfx.nodepath.get_pos() + lookahed_vec
        return self.mdt.phys.gnd_name(lookahead_pos)

    @property
    def left_right(self):
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
        brake = self.brake
        acceleration = False if brake else self.acceleration
        left, right = self.left_right
        return {'forward': acceleration, 'left': left, 'reverse': brake,
                'right': right}


class CarResultsAi(CarAi):

    def _end_async(self):
        pass
