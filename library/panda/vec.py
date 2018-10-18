from panda3d.core import Vec2 as PVec2, Vec3 as PVec3, Mat4, LVector2f, \
    LVector3f



class Panda2DVec(object):

    def __init__(self, x, y):
        self.vec = PVec2(x, y)

    def normalize(self):
        self.vec.normalize()
        return Panda2DVec(self.vec.x, self.vec.y)

    def signed_angle_deg(self, vec):
        return self.vec.signed_angle_deg(LVector2f(vec.x, vec.y))

    @property
    def x(self): return self.vec.x

    @property
    def y(self): return self.vec.y

    def dot(self, other): return self.vec.dot(other.vec)



class Panda3DVec(Panda2DVec):

    def __init__(self, x, y, z):
        self.vec = PVec3(x, y, z)

    def normalize(self):
        self.vec.normalize()
        return Panda3DVec(self.vec.x, self.vec.y, self.vec.z)

    def signed_angle_deg(self, vec, vec_up):
        return self.vec.signed_angle_deg(LVector3f(vec.x, vec.y, vec.z), vec_up)

    def rotate(self, deg):
        rot_mat = Mat4()
        rot_mat.set_rotate_mat(deg, (0, 0, 1))
        self.vec = rot_mat.xform_vec(self.vec)

    def __add__(self, vec):
        p3dvec = self.vec + vec.vec
        return Panda3DVec(p3dvec.x, p3dvec.y, p3dvec.z)

    def __sub__(self, vec):
        p3dvec = self.vec - vec.vec
        return Panda3DVec(p3dvec.x, p3dvec.y, p3dvec.z)

    def __neg__(self):
        p3dvec = - self.vec
        return Panda3DVec(p3dvec.x, p3dvec.y, p3dvec.z)

    def __mul__(self, val):
        p3dvec = self.vec * val
        return Panda3DVec(p3dvec.x, p3dvec.y, p3dvec.z)

    def length(self): return self.vec.length()

    @property
    def z(self): return self.vec.z

    @property
    def xy(self): return Panda2DVec(self.vec.x, self.vec.y)
