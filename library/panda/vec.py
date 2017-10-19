from panda3d.core import Vec2 as PVec2, Vec3 as PVec3, Mat4
from ..vec import Vec, Vec2


class Panda3DVec(Vec):

    def __init__(self, x, y, z):
        self.vec = PVec3(x, y, z)

    def rotate(self, deg):
        rot_mat = Mat4()
        rot_mat.set_rotate_mat(deg, (0, 0, 1))
        self.vec = rot_mat.xform_vec(self.vec)

    def __add__(a, b): return a.vec + b.vec

    def normalize(self):
        self.vec.normalize()
        return self.vec


class Panda2DVec(Vec2):

    def __init__(self, x, y):
        self.vec = PVec2(x, y)

    def normalize(self):
        self.vec.normalize()
        return self.vec

    def signed_angle_deg(self, vec):
        return self.vec.signed_angle_deg(vec)