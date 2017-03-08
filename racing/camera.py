from panda3d.core import Vec3, LVector3f


class Camera(object):

    speed = 50
    speed_slow = 20
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

    @staticmethod
    def new_val(val, tgt, incr):
        beyond = abs(val - tgt) > incr
        fit_p = lambda: val + (1 if tgt > val else -1) * incr
        return fit_p() if beyond else tgt

    def update(self, speed_ratio, is_rolling):
        curr_incr = self.speed * globalClock.getDt()
        curr_incr_slow = self.speed_slow * globalClock.getDt()
        dist_diff = self.dist_max - self.dist_min
        look_dist_diff = self.look_dist_max - self.look_dist_min
        z_diff = self.z_max - self.z_min
        look_z_diff = self.look_z_max - self.look_z_min

        z_u = Vec3(0, 1, 0)
        fwd_car_vec = eng.base.render.getRelativeVector(self.car_np, z_u)
        fwd_car_vec.normalize()
        fwd_vec = LVector3f(*self.cam_vec)
        fwd_vec.normalize()

        car_pos = self.car_np.get_pos()
        vec = -fwd_vec * (self.dist_min + dist_diff * speed_ratio)
        l_d_speed = self.look_dist_min + look_dist_diff * speed_ratio
        l_d = 0 if is_rolling else l_d_speed
        self.curr_l_d = self.new_val(self.curr_l_d, l_d, curr_incr_slow)
        tgt_vec = fwd_car_vec * self.curr_l_d
        delta_pos_z = self.z_min + z_diff * speed_ratio
        delta_cam_z = self.look_z_min + look_z_diff * speed_ratio

        #curr_cam_pos = car_pos + vec + (0, 0, delta_pos_z)
        #curr_cam_dist_fact = self.dist_min + dist_diff * speed_ratio
        #curr_occl = self.__occlusion_mesh(curr_cam_pos, curr_cam_dist_fact)
        #if curr_occl:
        #    occl_pos = curr_occl.getHitPos()
        #    vec = occl_pos - car_pos

        self.tgt_cam_x = car_pos.x + vec.x
        self.tgt_cam_y = car_pos.y + vec.y
        self.tgt_cam_z = car_pos.z + vec.z + delta_pos_z

        cam = eng.base.camera
        self.tgt_look_x, self.tgt_look_y, self.tgt_look_z = car_pos + tgt_vec
        new_x = self.new_val(cam.getX(), self.tgt_cam_x, curr_incr)
        new_y = self.new_val(cam.getY(), self.tgt_cam_y, curr_incr)
        new_z = self.new_val(cam.getZ(), self.tgt_cam_z, curr_incr_slow)

        # overwrite camera's position to set the physics
        #new_x = car_pos.x + 10
        #new_y = car_pos.y - 5
        #new_z = car_pos.z + 5

        if not is_rolling:
            eng.base.camera.setPos(new_x, new_y, new_z)
        look_z = self.tgt_look_z + delta_cam_z
        eng.base.camera.look_at(self.tgt_look_x, self.tgt_look_y, look_z)
        # facade

    #def __occlusion_mesh(self, pos, curr_cam_dist_fact):
    #    tgt = self.car.gfx.nodepath.getPos()
    #    occl = eng.phys.world_phys.rayTestClosest(pos, tgt)
    #    if not occl.hasHit():
    #        return
    #    occl_n = occl.getNode().getName()
    #    if occl_n not in ['Vehicle', 'Goal'] and curr_cam_dist_fact > .1:
    #        return occl

    @property
    def camera(self):
        return eng.base.camera

    def destroy(self):
        self.car = None
