from panda3d.core import Vec3, LVector3f
from yyagl.gameobject import GameObject


class Camera(GameObject):

    speed = 50
    speed_slow = 20
    speed_fast = 5000
    dist_min = 36
    dist_max = 72
    look_dist_min = 2
    look_dist_max = 16

    def __init__(self, car_np, cam_vec):
        self.car_np = car_np
        self.cam_vec = cam_vec  # eye to look_at
        self.curr_look_dist = 0
        self.curr_speed_ratio = 0
        self.fwd_car_vec = LVector3f(0, 0, 0)

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
        curr_incr = self.speed * globalClock.get_dt()
        curr_incr_slow = self.speed_slow * globalClock.get_dt()
        if is_fast:
            curr_incr_slow = self.speed_fast * globalClock.get_dt()
        dist_diff = self.dist_max - self.dist_min
        look_dist_diff = self.look_dist_max - self.look_dist_min

        fwd_car_vec = render.get_relative_vector(self.car_np, Vec3(0, 1, 0))
        fwd_car_vec.normalize()
        fwd_vec = LVector3f(*self.cam_vec)
        fwd_vec.normalize()
        fwd_incr = (.05 if is_rotating else .5) * globalClock.get_dt()
        self.fwd_car_vec = self.new_val_vec(self.fwd_car_vec, fwd_car_vec,
                                            fwd_incr)
        car_pos = self.car_np.get_pos()
        vec = -fwd_vec * (self.dist_min + dist_diff * self.curr_speed_ratio)
        l_d_speed = self.look_dist_min + look_dist_diff * self.curr_speed_ratio
        l_d = 0 if is_rolling else l_d_speed
        self.curr_look_dist = self.new_val(self.curr_look_dist, l_d,
                                           curr_incr_slow)
        tgt_vec = self.fwd_car_vec * self.curr_look_dist

        # curr_cam_pos = car_pos + vec + (0, 0, delta_pos_z)
        # curr_cam_dist_fact = self.dist_min + dist_diff * speed_ratio
        # curr_occl = self.__occlusion_mesh(curr_cam_pos, curr_cam_dist_fact)
        # if curr_occl:
        #     occl_pos = curr_occl.getHitPos()
        #     vec = occl_pos - car_pos

        c_i = curr_incr_slow if is_fast else curr_incr
        cam_pos = self.eng.base.camera.get_pos()
        new_pos = self.new_val_vec(cam_pos, car_pos + vec, c_i)
        # overwrite camera's position to set the physics
        # new_pos = (car_pos.x + 10, car_pos.y - 5, car_pos.z + 5
        if not is_rolling:
            self.eng.base.camera.set_pos(new_pos)
        self.eng.base.camera.look_at(car_pos + tgt_vec)

    # def __occlusion_mesh(self, pos, curr_cam_dist_fact):
    #     tgt = self.car.gfx.nodepath.getPos()
    #     occl = eng.phys.world_phys.rayTestClosest(pos, tgt)
    #     if not occl.hasHit():
    #         return
    #     occl_n = occl.getNode().getName()
    #     if occl_n not in ['Vehicle', 'Goal'] and curr_cam_dist_fact > .1:
    #         return occl

    @property
    def camera(self):
        return self.eng.base.camera

    @staticmethod
    def render_all():  # workaround for premunge_scene in 1.9
        Camera.eng.base.camera.set_pos(0, 0, 10000)
        Camera.eng.base.camera.look_at(0, 0, 0)
        track_model = game.logic.season.race.logic.track.gfx.model
        skydome = track_model.find('**/OBJSkydome*')
        skydome and skydome.hide()
        base.graphicsEngine.render_frame()
        base.graphicsEngine.render_frame()
        skydome and skydome.show()

    def destroy(self):
        pass
