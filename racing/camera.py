from math import cos, pi
from panda3d.core import Vec3, LVector3f
from yyagl.gameobject import GameObject


class Camera(GameObject):

    speed = 50
    inertia_dist = 15
    speed_slow = 20
    speed_fast = 5000
    dist_min = 24
    dist_max = 48
    look_dist_min = 2
    look_dist_max = 16
    overwrite = [0, 0, 0]

    def __init__(self, car_np, cam_vec, car):
        GameObject.__init__(self)
        self.car_np = car_np
        self.cam_vec = cam_vec  # eye to look_at
        self.curr_look_dist = 0
        self.curr_speed_ratio = 0
        self.fwd_car_vec = LVector3f(0, 0, 0)
        self.curr_dist = 0
        self.curr_h = 0
        self.car = car

    def ease(self, val):
        if val <= 0: return 0
        elif val >= 1: return 1
        else: return 1 - cos(val * pi)

    def curr_speed(self, pos, tgt):
        dist = (tgt - pos).length()
        inertia_fact = max(0, min(1, self.ease(dist / self.inertia_dist))) if dist else 0
        return self.speed * inertia_fact

    @staticmethod
    def new_val(val, tgt, incr):
        beyond = abs(val - tgt) < incr
        next_val = lambda: val + (1 if tgt > val else -1) * incr
        return tgt if beyond else next_val()

    @staticmethod
    def new_val_vec(vec_val, vec_tgt, incr):
        val_els = [vec_val.x, vec_val.y, vec_val.z]
        tgt_els = [vec_tgt.x, vec_tgt.y, vec_tgt.z]
        res = []
        for val, tgt in zip(val_els, tgt_els):
            beyond = abs(val - tgt) > incr
            fit_p = lambda val=val, tgt=tgt: \
                val + (1 if tgt > val else -1) * incr
            res += [fit_p() if beyond else tgt]
        return LVector3f(* res)

    def update(self, speed_ratio, is_rolling, is_fast, is_rotating):
        self.curr_speed_ratio = self.new_val(
            self.curr_speed_ratio, speed_ratio, 1 * globalClock.get_dt())
        dist_diff = self.dist_max - self.dist_min
        look_dist_diff = self.look_dist_max - self.look_dist_min
        fwd_car_vec = self.eng.gfx.root.get_relative_vector(self.car_np, Vec3(0, 1, 0))
        fwd_car_vec.normalize()
        fwd_incr = (.05 if is_rotating else .5) * globalClock.get_dt()
        self.fwd_car_vec = self.new_val_vec(self.fwd_car_vec, fwd_car_vec,
                                            fwd_incr)
        dincr = 10.0 * globalClock.getDt()
        self.curr_dist = self.new_val(
            self.curr_dist, self.dist_min + dist_diff * self.curr_speed_ratio,
            dincr)
        back_car_vec = -fwd_car_vec * self.curr_dist
        back_car_vec += (0, 0,
                         self.dist_min + dist_diff * self.curr_speed_ratio)
        back_incr = (.05 if is_rotating else 25.0) * globalClock.get_dt()
        car_pos = self.car_np.get_pos()
        l_d_speed = self.look_dist_min + look_dist_diff * self.curr_speed_ratio
        l_d = 0 if is_rolling else l_d_speed
        cam_pos = base.camera.get_pos()
        curr_incr = self.curr_speed(cam_pos, car_pos + back_car_vec) * globalClock.get_dt()
        curr_incr_slow = self.speed_slow * globalClock.get_dt()
        if is_fast:
            curr_incr_slow = self.speed_fast * globalClock.get_dt()
        self.curr_look_dist = self.new_val(self.curr_look_dist, l_d,
                                           curr_incr_slow)
        tgt_vec = self.fwd_car_vec * self.curr_look_dist



        curr_wp = self.car.logic.closest_wp().next
        if curr_wp.node.has_tag('camera'):
            cam_forced_pos = curr_wp.node.get_tag('camera')
            cam_forced_pos = cam_forced_pos.split(',')
            cam_forced_pos = (float(elm) for elm in cam_forced_pos)
            cam_forced_pos = Vec3(*cam_forced_pos)
            cam_forced_vec = cam_forced_pos - curr_wp.pos
            cam_forced_vec.normalize()
            cam_forced_vec *= back_car_vec.length()
            back_car_vec = cam_forced_vec

        c_i = curr_incr_slow if is_fast else curr_incr
        new_pos = self.new_val_vec(cam_pos, car_pos + back_car_vec, c_i)
        # overwrite camera's position to set the physics
        if any(val for val in self.overwrite):
            ovw = self.overwrite
            new_pos = (car_pos.x + ovw[0], car_pos.y + ovw[1], car_pos.z + ovw[2])
        if not is_rolling: base.camera.set_pos(new_pos)
        base.camera.look_at(car_pos + tgt_vec)

    @property
    def camera(self): return base.camera

    @staticmethod
    def render_all(track_model):  # workaround for premunge_scene in 1.9
        base.camera.set_pos(0, 0, 10000)
        base.camera.look_at(0, 0, 0)
        skydome = track_model.find('**/OBJSkydome*')
        skydome and skydome.hide()
        base.graphicsEngine.render_frame()
        base.graphicsEngine.render_frame()
        skydome and skydome.show()

    def destroy(self):
        GameObject.destroy(self)
