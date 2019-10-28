from logging import info
from math import cos, pi
from panda3d.core import Vec3, LVector3f, Mat4
from yyagl.gameobject import GameObject
from yyagl.engine.vec import Vec2, Vec


class Camera(GameObject):

    speed = 50
    inertia_dist = 15
    speed_slow = 20
    speed_fast = 5000
    dist_min = 24
    dist_max = 48  # 24
    look_dist_min = 2  # 0
    look_dist_max = 16  # 0
    overwrite = [0, 0, 0]  # [8, 8, 1]

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
        base.camLens.set_near_far(1.0, 1000.0)

    @staticmethod
    def ease(val):
        if val <= 0: return 0
        elif val >= 1: return 1
        else: return 1 - cos(val * pi)

    def curr_speed(self, pos, tgt):
        dist = (tgt - pos).length()
        easeval = self.ease(dist / self.inertia_dist)
        inertia_fact = max(0, min(1, easeval)) if dist else 0
        return self.speed * inertia_fact

    def get_camera(self):
        regions = base.win.get_active_display_regions()
        if self.eng.cfg.dev_cfg.shaders_dev:
            return self.eng.shader_mgr.filter_mgr.camera
        return regions[self.car.player_car_idx].get_camera()

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

    @property
    def _back_vec_z(self):
        dist_diff = self.dist_max - self.dist_min
        return self.dist_min + dist_diff * self.curr_speed_ratio

    def _new_pos(self, look_at_pos, back_car_vec, curr_l, c_i_length, c_i_rot):
        d_t = globalClock.get_dt()
        cam_pos = self.get_camera().get_pos()
        vec = cam_pos - look_at_pos
        prj_vec = Vec3(vec.x, vec.y, 0).normalized()
        prj_back_car_vec = Vec3(back_car_vec.x, back_car_vec.y, 0).normalized()
        angle = prj_vec.signed_angle_deg(prj_back_car_vec, (0, 0, 1))
        rot_angle = self.new_val(0, angle, c_i_rot)
        new_vec = prj_vec.normalized()
        rot_new_vec = self.__rotate(new_vec, rot_angle * d_t)
        new_vec_l = self.new_val(prj_vec.length(), prj_back_car_vec.length(), c_i_length * d_t)
        new_vec = rot_new_vec * curr_l
        new_pos = look_at_pos + new_vec
        new_pos.z = self.new_val(cam_pos.z, look_at_pos.z + back_car_vec.z, 8 * d_t)
        return new_pos

    def __rotate(self, vec, deg):
        rot_mat = Mat4()
        rot_mat.set_rotate_mat(deg, (0, 0, 1))
        return rot_mat.xform_vec(vec)

    def update(self, speed_ratio, is_rolling, is_fast, is_rotating):
        d_t = globalClock.get_dt()
        self.curr_speed_ratio = self.new_val(self.curr_speed_ratio, speed_ratio,
                                             1 * d_t)
        dist_diff = self.dist_max - self.dist_min
        look_dist_diff = self.look_dist_max - self.look_dist_min
        gfx_root = self.eng.gfx.root
        fwd_car_vec = gfx_root.get_relative_vector(self.car_np, Vec3(0, 1, 0))
        fwd_car_vec.normalize()
        fwd_incr = (.05 if is_rotating else .5) * d_t
        self.fwd_car_vec = self.new_val_vec(self.fwd_car_vec, fwd_car_vec,
                                            fwd_incr)
        self.curr_dist = self.new_val(
            self.curr_dist, self.dist_min + dist_diff * self.curr_speed_ratio,
            10.0 * d_t)
        back_car_vec = -fwd_car_vec * self.curr_dist
        car_pos = self.car_np.get_pos()
        back_car_vec += (0, 0, self._back_vec_z)
        tmp_back_pos = car_pos + back_car_vec
        curr_gnd_h = self.gnd_height(tmp_back_pos)
        if curr_gnd_h and tmp_back_pos.z < curr_gnd_h + .5:
            back_car_vec.z = curr_gnd_h - car_pos.z + .5
        l_d_speed = self.look_dist_min + look_dist_diff * self.curr_speed_ratio
        l_d = 0 if is_rolling else l_d_speed
        cam_pos = self.get_camera().get_pos()

        curr_incr = self.curr_speed(cam_pos, car_pos + back_car_vec) * d_t
        curr_incr_slow = self.speed_slow * d_t
        if is_fast: curr_incr_slow = self.speed_fast * d_t
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
        look_at_pos = car_pos + tgt_vec
        new_pos = self._new_pos(look_at_pos, back_car_vec, self.curr_dist, c_i, 20)
        # overwrite camera's position to set the physics
        if any(val for val in self.overwrite):
            ovw = self.overwrite
            new_pos = car_pos.x + ovw[0], car_pos.y + ovw[1], car_pos.z + ovw[2]
        if not is_rolling: self.get_camera().set_pos(new_pos)
        self.get_camera().look_at(car_pos + tgt_vec)

    @property
    def camera(self): return self.get_camera()

    def gnd_height(self, pos):
        phys_root = self.eng.phys_mgr.root
        bottompos = pos - (0, 0, 100)
        bottom = Vec(bottompos.x, bottompos.y, bottompos.z)
        toppos = pos + (0, 0, 100)
        top = Vec(toppos.x, toppos.y, toppos.z)
        hits = phys_root.ray_test_all(bottom, top)
        for hit in hits.get_hits():
            prefs = ['RoadOBJ', 'OffroadOBJ']
            if any(hit.getNode().getName().startswith(pref) for pref in prefs):
                return hit.getHitPos().z

    #def render_all(self, track_model):  # workaround for premunge_scene in 1.9
        #self.get_camera().set_pos(0, 0, 10000)
        #self.get_camera().look_at(0, 0, 0)
        #skydome = track_model.find('**/OBJSkydome*')
        #info('skydome %sfound' % ('' if skydome else 'not '))
        #if skydome: skydome.hide()
        #base.graphicsEngine.render_frame()
        #base.graphicsEngine.render_frame()
        #if skydome: skydome.show()

    def destroy(self):
        GameObject.destroy(self)


class FPCamera(Camera):

    dist_min = 16
    dist_max = 24
    height = 8

    def __init__(self, car_np, cam_vec, car):
        Camera.__init__(self, car_np, cam_vec, car)

    def _new_pos(self, back_car_vec, c_i):
        car_pos = self.car_np.get_pos()
        curr_cam_pos = car_pos + back_car_vec
        curr_occl = self.__occlusion_mesh(curr_cam_pos)
        is_occl = False
        if curr_occl:
            occl_pos = curr_occl.getHitPos()
            back_car_vec = occl_pos - car_pos
            is_occl = True
        if not is_occl:
            cam_vec = car_pos - curr_cam_pos
            look_at_pos = car_pos  # + tgt_vec
            new_pos = Camera._new_pos(self, look_at_pos, back_car_vec, self.curr_dist, c_i, 20)
        else:
            new_pos = occl_pos
        return new_pos

    @property
    def _back_vec_z(self):
        return self.height

    def __occlusion_mesh(self, pos):
        tgt = self.car.gfx.nodepath.get_pos()
        occl = self.__closest_occl(pos, tgt)
        if not occl:
            return
        car_vec = self.car.logic.car_vec
        rot_mat_left = Mat4()
        rot_mat_left.setRotateMat(90, (0, 0, 1))
        car_vec_left = rot_mat_left.xformVec(car_vec._vec)
        tgt_left = tgt + car_vec_left
        pos_left = pos + car_vec_left
        occl_left = self.__closest_occl(pos_left, tgt_left)
        if not occl_left:
            return
        rot_mat_right = Mat4()
        rot_mat_right.setRotateMat(-90, (0, 0, 1))
        car_vec_right = rot_mat_right.xformVec(car_vec._vec)
        car_vec_right += (0, 0, 2)
        tgt_right = tgt + car_vec_right
        pos_right = pos + car_vec_right
        phys_root = self.eng.phys_mgr.root
        occl_right = phys_root.ray_test_closest(tgt_right, pos_right)
        occl_right = self.__closest_occl(pos_right, tgt_right)
        if not occl_right:
            return
        return occl

    def __closest_occl(self, pos, tgt):
        occl = None
        dist = 9999
        tgtv = Vec(tgt.x, tgt.y, tgt.z)
        posv = Vec(pos.x, pos.y, pos.z)
        occl_l = self.eng.phys_mgr.root.ray_test_all(tgtv, posv)  # , mask)
        for _occl in occl_l.get_hits():
            if _occl.getNode().getName() not in ['Vehicle', 'Goal']:
                if (Vec(*_occl.getHitPos()) - tgtv).length() < dist:
                    dist = (Vec(*_occl.getHitPos()) - tgtv).length()
                    occl = _occl
        return occl
