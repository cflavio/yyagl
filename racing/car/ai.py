from random import uniform
from panda3d.core import Vec3, LineSegs, LPoint3f
from yyagl.gameobject import AiColleague, GameObject
from yyagl.computer_proxy import ComputerProxy, once_a_frame
from yyagl.engine.vec import Vec


class ObstInfo(object):

    def __init__(self, name, dist):
        self.name = name
        self.dist = dist


class LastObstInfo(object):

    def __init__(self, direction, time):
        self.direction = direction
        self.time = time


class DirKeys(object):

    def __init__(self, forward, left, rear, right):
        self.forward = forward
        self.left = left
        self.rear = rear
        self.right = right


class CarAiPoller(object):

    def __init__(self):
        self.idx = 0

    def set_cars(self, cars):
        self.cars = cars

    def tick(self):
        if not self.cars: return
        self.idx = (self.idx + 1) % len(self.cars)

    @property
    def current(self):
        if not hasattr(self, 'cars') or not self.cars: return 0
        return self.cars[self.idx]

    def destroy(self):
        self.cars = None


class DebugLines(object):

    def __init__(self, color):
        self.color = color
        self.lines = []

    def clear(self):
        map(lambda line: line.remove_node(), self.lines)
        self.lines = []

    def draw(self, start, end):
        segs = LineSegs()
        segs.set_color(*self.color)
        segs.moveTo(start)
        segs.drawTo(end)
        segs_node = segs.create()
        self.lines += [render.attachNewNode(segs_node)]

    def destroy(self):
        self.clear()


class AbsAiLogic(ComputerProxy, GameObject):

    def __init__(self, car, cars, player_car):
        GameObject.__init__(self)
        self.car = car
        self.cars = cars
        self.player_car = player_car
        self._sectors = ['center', 'left', 'right']
        self._curr_sector = 0  # i.e. center
        self.sector2samples_gnd = {'left': [''], 'center': [''], 'right': ['']}
        self.sector2obsts = {'left': [], 'center': [], 'right': []}
        bnds = car.phys.coll_mesh.get_tight_bounds()  # (lowerleft, upperright)
        self.width_bounds = (bnds[0].x * 1.15, bnds[1].x * 1.15)
        whl_height = max(whl.get_wheel_radius()
                         for whl in car.phys.vehicle.get_wheels())
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
        return Vec(*(self.curr_tgt_wp.get_pos() - self.car.pos)).normalize()

    def _update_gnd(self, direction, hit_res):  # direction in left, center, right
        if not hit_res: return
        if len(self.sector2samples_gnd[direction]) > 0:
            self.sector2samples_gnd[direction].pop(0)
        self.sector2samples_gnd[direction] += [hit_res[0][0]]

    def get_obstacles(self):
        left_samples = [smp for smp in self.sector2obsts['left'] if smp.dist]
        right_samples = [smp for smp in self.sector2obsts['right'] if smp.dist]
        center_samples = [smp
                          for smp in self.sector2obsts['center'] if smp.dist]
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
        for direction in ['center', 'left', 'right']:
            for smp in self.sector2obsts[direction][:]:
                if smp.name == 'Vehicle':
                    self.sector2obsts[direction].remove(smp)

    def _update_obst(self, direction, hit_res):
        nsam = 0  # 0 if self.car.phys.speed >= 5 else 10
        if len(self.sector2obsts[direction]) > nsam:
            del self.sector2obsts[direction][:-(nsam - 2)]
        if hit_res: self.sector2obsts[direction] += [ObstInfo(*hit_res[0])]

    def hit_res(self, direction):
        lat_sector_deg = 40 - 35 * self.car.phys.speed_ratio
        sector2bounds = {'left': (0, lat_sector_deg), 'center': (0, 0),
                         'right': (-lat_sector_deg, 0)}
        if direction == 'center':
            offset_y = Vec(uniform(*self.width_bounds), 0, 0)
        else:
            offset_y = Vec(self.width_bounds[self.bnd_idx(direction)], 0, 0)
        start = Vec(*(self.car.pos - self.car_vec * .8))
        offset_y.rotate(self.car.heading)
        half = (self.height_bounds[0] + self.height_bounds[1]) / 4
        start = start + offset_y + (0, 0, uniform(half, self.height_bounds[1]))
        lgt = 4 + 41 * self.car.phys.speed_ratio
        lookahed_vec = Vec(*(self.car_vec * lgt))
        deg = uniform(*sector2bounds[direction])
        lookahed_vec.rotate(deg)
        lookahead_pos = Vec(*(self.car.pos)) + lookahed_vec + (0, 0, self.height_bounds[0] - 2)
        hit_res = self.eng.phys_mgr.ray_test_all(start, lookahead_pos, self.car.logic.bitmask)
        result = []
        for hit in hit_res.get_hits():
            result += [(hit.get_node().get_name(), (start - hit.get_hit_pos()).length())]
        result = sorted(result, key=lambda elm: elm[1])
        if self.car.fsm.getCurrentOrNextState() != 'Results' and \
                self.player_car == self.car.name:
            self.debug_lines_obst.draw(start, lookahead_pos)
        road_res = [res for res in result if any(road_n in res[0] for road_n in ['Road', 'Offroad'])][:1]
        obs_res = [res for res in result if not any(road_n in res[0] for road_n in ['Road', 'Offroad'])][:1]
        return road_res, obs_res

    def destroy(self):
        self.car = None
        self.debug_lines_gnd.destroy()
        self.debug_lines_obst.destroy()
        ComputerProxy.destroy(self)
        GameObject.destroy(self)


class FrontAiLogic(AbsAiLogic):

    @property
    def curr_tgt_wp(self):  # no need to be cached
        return self.car.logic.closest_wp().next

    @property
    def car_vec(self):
        return self.car.logic.car_vec

    @staticmethod
    def bnd_idx(direction):
        return 0 if direction == 'left' else 1

    def on_brake(self, dist_center, dist_left, dist_right):
        left = right = False
        min_dist = min([dist_center, dist_left, dist_right])
        if not(min_dist < 5 and self.car.phys.speed < 0):
            return
        if dist_left == min_dist:
            left = True
        elif dist_right == min_dist:
            right = True
        return left, right, dist_left < 4, dist_right < 4


class RearAiLogic(AbsAiLogic):

    @property
    def curr_tgt_wp(self):  # no need to be cached
        return self.car.logic.closest_wp().prev

    @property
    def car_vec(self):
        return -self.car.logic.car_vec

    @staticmethod
    def bnd_idx(direction):
        return 1 if direction == 'left' else 0

    def on_brake(self, dist_center, dist_left, dist_right):
        pass


class CarAi(AiColleague, ComputerProxy):

    def __init__(self, mediator, car_props):
        AiColleague.__init__(self, mediator)
        ComputerProxy.__init__(self)
        race_props = car_props.race_props
        player_car_name = race_props.season_props.player_car_name
        self.road_name = race_props.road_name
        self.waypoints = car_props.track_waypoints
        self.ai_poller = car_props.ai_poller
        self.cars = race_props.season_props.car_names
        self.front_logic = FrontAiLogic(self.mediator, self.cars, player_car_name)
        self.rear_logic = RearAiLogic(self.mediator, self.cars, player_car_name)
        self.last_positions = []
        # last 12 positions (a position a second) for respawning if the car
        # can't move
        self.last_pos_time = 0  # time of the last sampling pos
        self.last_obst_info = LastObstInfo(None, 0)  # (is_l, is_r), time
        self.eng.attach_obs(self.on_frame)

    @property
    def curr_logic(self):
        obst = list(self.front_logic.get_obstacles())
        if self.mediator.phys.speed < 20 and obst[0].name and obst[0].dist < 4:
            return self.rear_logic
        return self.front_logic

    def __eval_gnd(self):
        ratio_road = lambda samples: float(
            self.__n_samples_on_road(samples)) / len(samples)
        ratio_left = ratio_road(self.curr_logic.sector2samples_gnd['left'])
        ratio_center = ratio_road(self.curr_logic.sector2samples_gnd['center'])
        ratio_right = ratio_road(self.curr_logic.sector2samples_gnd['right'])
        ratios = [ratio_center, ratio_left, ratio_right]
        ratio_max = max(ratios)
        if ratio_left < .3 and ratio_right > .6:
            return 'right'
        elif ratio_right < .3 and ratio_left > .6:
            return 'left'
        return ['center', 'left', 'right'][ratios.index(ratio_max)]

    def __n_samples_on_road(self, samples):
        return len([smp for smp in samples if smp.startswith(self.road_name)])

    def on_frame(self):
        if self.ai_poller.current != self.mediator.name: return
        self._eval_respawn()
        for logic in [self.front_logic, self.rear_logic]:
            logic.debug_lines_gnd.clear()
            logic.debug_lines_obst.clear()
        directions = [self.front_logic._sectors[self.front_logic._curr_sector]]
        self.front_logic._curr_sector = (self.front_logic._curr_sector + 1) % 3
        hit_res = self.front_logic.hit_res(directions[0])
        self.front_logic._update_gnd(directions[0], hit_res[0])
        self.front_logic.clear()
        self.front_logic._update_obst(directions[0], hit_res[1])
        if self.mediator.phys.speed < 10 or self.mediator.logic.has_rear_weapon:
            hit_res = self.rear_logic.hit_res(directions[0])
            self.rear_logic._update_gnd(directions[0], hit_res[0])
            self.rear_logic._update_obst(directions[0], hit_res[1])

    def _eval_respawn(self):
        if self.mediator.fsm.getCurrentOrNextState() in ['Loading', 'Countdown']:
            return
        if self.eng.curr_time - self.last_pos_time < 1:
            return
        self.last_pos_time = self.eng.curr_time
        self.last_positions += [self.mediator.gfx.nodepath.get_pos()]
        if len(self.last_positions) <= 12:
            return
        self.last_positions.pop(0)
        npos = len(self.last_positions)
        center_x = sum(pos.x for pos in self.last_positions) / npos
        center_y = sum(pos.y for pos in self.last_positions) / npos
        center_z = sum(pos.z for pos in self.last_positions) / npos
        center = LPoint3f(center_x, center_y, center_z)
        if all((pos - center).length() < 6 for pos in self.last_positions):
            self.last_positions = []
            self.mediator.event.process_respawn()

    def brake(self, obstacles, obstacles_back):
        closest_center, closest_left, closest_right = obstacles
        closest_center_b, closest_left_b, closest_right_b = obstacles_back
        dist_thr_c = 4 if closest_center.name == 'Vehicle' else 8
        dist_thr_l = 4 if closest_left.name == 'Vehicle' else 8
        dist_thr_r = 4 if closest_right.name == 'Vehicle' else 8
        if self.mediator.phys.speed < 0:
            is_closer_c = closest_center.dist < dist_thr_c
            is_closer_l = closest_left.dist < dist_thr_l
            is_closer_r = closest_right.dist < dist_thr_r
            is_closer = is_closer_c or is_closer_l or is_closer_r
            if is_closer and closest_center_b.dist > 2:
                return True
        else:
            dist_thr = 1 if closest_center.name == 'Vehicle' else 5
            dist_thr_c = 3 + dist_thr * self.mediator.phys.speed_ratio
            if closest_center.dist < dist_thr_c and closest_center_b.dist > 2:
                return True
        if self.mediator.phys.speed < 40:
            return False
        return self.curr_logic.car_dot_traj < .4

    @property
    def is_on_road(self):
        grounds = self.mediator.phys.gnd_names
        return all(name.startswith(self.road_name) for name in grounds)

    @property
    def acceleration(self):
        if self.mediator.phys.speed < 40:
            return True
        if not self.is_on_road:
            return False
        return self.curr_logic.car_dot_traj > .8

    def left_right(self, obstacles, brake, obstacles_back):
        if self.eng.curr_time - self.last_obst_info.time < .05:
            return self.last_obst_info.direction
        curr_obs = obstacles_back if brake and self.mediator.phys.speed < 10 else \
            obstacles
        closest_center, closest_left, closest_right = curr_obs
        thr_far = 4 + self.mediator.phys.speed_ratio * 8
        thr_close = 2 + self.mediator.phys.speed_ratio * 2
        if brake and self.mediator.phys.speed < 10:
            thr_far = 12
            thr_close = 4
        obst_center = closest_center.dist < thr_far
        obst_left = closest_left.dist < thr_far
        obst_right = closest_right.dist < thr_far
        has_obst_left = closest_left.dist < thr_close
        has_obst_right = closest_right.dist < thr_close
        obst_center_back = closest_center.dist < thr_far
        obst_left_back = closest_left.dist < thr_far
        obst_right_back = closest_right.dist < thr_far
        has_obst_left_back = closest_left.dist < thr_close
        has_obst_right_back = closest_right.dist < thr_close
        car_vec = self.mediator.logic.car_vec
        tgt = Vec3(self.curr_logic.tgt_vec.x, self.curr_logic.tgt_vec.y, 0)
        tgt_x_car = tgt.cross(Vec3(car_vec.x, car_vec.y, 0))
        dot_res = tgt_x_car.dot(Vec3(0, 0, 1))

        # evaluate backward
        if self.curr_logic.car_dot_traj < -.2:
            left, right = dot_res < 0, dot_res >= 0
            if brake and self.mediator.phys.speed < 10:
                left = left and not has_obst_left_back
                right = right and not has_obst_right_back
                if left or right:
                    return left, right
            elif not brake:
                left = left and not has_obst_left
                right = right and not has_obst_right
                if left or right:
                    return left, right

        # evaluate obstacles
        if brake and self.mediator.phys.speed < 10:
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
            if brake and self.mediator.phys.speed < 10:
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
                self.last_obst_info = LastObstInfo((left, right),
                                                   self.eng.curr_time)
                return left, right

        # evaluate on_road
        gnd_dir = self.__eval_gnd()
        if gnd_dir == 'left':
            if brake and self.mediator.phys.speed < 10 and not curr_has_obs_left:
                return False, True
            elif brake and self.mediator.phys.speed < 10 and not curr_has_obs_right:
                return True, False
            elif not brake and not curr_has_obs_left:
                return True, False
            elif not brake and not curr_has_obs_right:
                return False, True
        elif gnd_dir == 'right':
            if brake and self.mediator.phys.speed < 10 and not curr_has_obs_left:
                return True, False
            elif brake and self.mediator.phys.speed < 10 and not curr_has_obs_right:
                return False, True
            elif not brake and not curr_has_obs_left:
                return False, True
            elif not brake and not curr_has_obs_right:
                return True, False

        # evaluate waypoints
        # if self.mediator.name == game.player_car.name:
        #     print 'dot', self.curr_logic.car_dot_traj
        if abs(self.curr_logic.car_dot_traj) > .98:
            return False, False
        car_vec = self.curr_logic.car_vec
        if brake and self.mediator.phys.speed < 10:
            left, right = dot_res >= 0, dot_res < 0
        else:
            left, right = dot_res < 0, dot_res >= 0
        if brake and self.mediator.phys.speed < 10:
            if left and curr_has_obs_right:
                left = False
            if right and curr_has_obs_left:
                right = False
        elif not brake:
            if left and curr_has_obs_left:
                left = False
            if right and curr_has_obs_right:
                right = False
        return left, right

    @once_a_frame
    def get_input(self):
        # import time; time.sleep(.01)
        # if self.mediator.name == game.player_car.name:
        #     print 'dot_prod', self.car_dot_traj
        # if self.mediator.name == game.player_car.name:
        #     print 'speed', self.mediator.phys.speed
        obstacles = list(self.front_logic.get_obstacles())
        # if self.mediator.name == game.player_car.name:
        #     print 'obstacles', obstacles
        obstacles_back = list(self.rear_logic.get_obstacles())
        # if self.mediator.name == game.player_car.name:
        #     print 'obstacles_back', obstacles_back
        brake = self.brake(obstacles, obstacles_back)
        # if self.mediator.name == game.player_car.name:
        #    print 'brake', brake
        acceleration = False if brake else self.acceleration
        # if self.mediator.name == game.player_car.name:
        #     print 'acceleration', acceleration
        left, right = self.left_right(obstacles, brake, obstacles_back)
        # if self.mediator.name == game.player_car.name:
        #     print 'left, right', left, right
        # if self.mediator.name == game.player_car.name:
        #     print self.__eval_gnd()
        # if self.mediator.name == game.player_car.name:
        #     print left, right, brake, acceleration, self.__eval_gnd(), \
        #         self.front_logic.car_dot_traj, self.mediator.phys.speed, \
        #         obstacles, obstacles_back
        if self.mediator.logic.weapon and self.mediator.logic.weapon.ai_fire():
            self.mediator.logic.fire()
        return DirKeys(acceleration, left, brake, right)

    def destroy(self):
        self.eng.detach_obs(self.on_frame)
        map(lambda logic: logic.destroy(), [self.front_logic, self.rear_logic])
        AiColleague.destroy(self)
        ComputerProxy.destroy(self)


class CarResultsAi(CarAi):

    def _end_async(self):
        pass
