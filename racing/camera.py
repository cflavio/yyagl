from panda3d.core import Vec3, LVector3f


class Camera(object):

    speed = 50
    speed_slow = 20
    speed_fast = 5000
    dist_min = 36
    dist_max = 72
    z_max = 5
    z_min = 3
    look_dist_min = 2
    look_dist_max = 16
    look_z_max = 2
    look_z_min = 0

    def __init__(self, car_np, cam_vec):
        self.car_np = car_np
        self.cam_vec = cam_vec
        self.tgt_cam_x = None
        self.tgt_cam_y = None
        self.tgt_cam_z = None
        self.tgt_look_x = None
        self.tgt_look_y = None
        self.tgt_look_z = None
        self.curr_l_d = 0
        self.curr_speed_ratio = 0
        self.fwd_car_vec = LVector3f(0, 0, 0)

    @staticmethod
    def new_val(val, tgt, incr):
        beyond = abs(val - tgt) > incr
        fit_p = lambda: val + (1 if tgt > val else -1) * incr
        return fit_p() if beyond else tgt

    @staticmethod
    def new_val_vec(vec_val, vec_tgt, incr):
        val_els = [vec_val.x, vec_val.y, vec_val.z]
        tgt_els = [vec_tgt.x, vec_tgt.y, vec_tgt.z]
        res = []
        for val, tgt in zip(val_els, tgt_els):
            beyond = abs(val - tgt) > incr
            fit_p = lambda: val + (1 if tgt > val else -1) * incr
            res += [fit_p() if beyond else tgt]
        return LVector3f(* res)

    def update(self, speed_ratio, is_rolling, fast, is_rotating):
        self.curr_speed_ratio = self.new_val(
            self.curr_speed_ratio, speed_ratio, 1 * globalClock.getDt())
        curr_incr = self.speed * globalClock.getDt()
        curr_incr_slow = self.speed_slow * globalClock.getDt()
        if fast:
            curr_incr_slow = self.speed_fast * globalClock.getDt()
        dist_diff = self.dist_max - self.dist_min
        look_dist_diff = self.look_dist_max - self.look_dist_min
        z_diff = self.z_max - self.z_min
        look_z_diff = self.look_z_max - self.look_z_min

        z_u = Vec3(0, 1, 0)
        fwd_car_vec = render.getRelativeVector(self.car_np, z_u)
        fwd_car_vec.normalize()
        fwd_vec = LVector3f(*self.cam_vec)
        fwd_vec.normalize()
        fwd_incr = (.05 if is_rotating else .5) * globalClock.getDt()
        self.fwd_car_vec = self.new_val_vec(self.fwd_car_vec, fwd_car_vec,
                                            fwd_incr)
        car_pos = self.car_np.get_pos()
        vec = -fwd_vec * (self.dist_min + dist_diff * self.curr_speed_ratio)
        l_d_speed = self.look_dist_min + look_dist_diff * self.curr_speed_ratio
        l_d = 0 if is_rolling else l_d_speed
        self.curr_l_d = self.new_val(self.curr_l_d, l_d, curr_incr_slow)
        tgt_vec = self.fwd_car_vec * self.curr_l_d
        delta_pos_z = self.z_min + z_diff * self.curr_speed_ratio
        delta_cam_z = self.look_z_min + look_z_diff * self.curr_speed_ratio

        # curr_cam_pos = car_pos + vec + (0, 0, delta_pos_z)
        # curr_cam_dist_fact = self.dist_min + dist_diff * speed_ratio
        # curr_occl = self.__occlusion_mesh(curr_cam_pos, curr_cam_dist_fact)
        # if curr_occl:
        #     occl_pos = curr_occl.getHitPos()
        #     vec = occl_pos - car_pos

        self.tgt_cam = car_pos + vec + (0, 0, delta_pos_z)
        self.tgt_look_x, self.tgt_look_y, self.tgt_look_z = car_pos + tgt_vec
        c_i = curr_incr_slow if fast else curr_incr
        cam = eng.base.camera
        new_pos = self.new_val_vec(cam.get_pos(), self.tgt_cam, c_i)
        # overwrite camera's position to set the physics
        # new_pos = (car_pos.x + 10, car_pos.y - 5, car_pos.z + 5
        if not is_rolling:
            eng.base.camera.setPos(new_pos)
        look_z = self.tgt_look_z + delta_cam_z
        eng.base.camera.look_at(self.tgt_look_x, self.tgt_look_y, look_z)

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
        return eng.base.camera

    @staticmethod
    def render_all():
        eng.base.camera.setPos(0, 0, 10000)
        eng.base.camera.look_at(0, 0, 0)
        track_model = game.logic.season.race.logic.track.gfx.model
        skydome = track_model.find('**/OBJSkydome*')
        skydome and skydome.hide()
        base.graphicsEngine.renderFrame()
        base.graphicsEngine.renderFrame()
        skydome and skydome.show()

    def destroy(self):
        pass
