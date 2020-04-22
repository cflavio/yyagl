from panda3d.core import Vec2, Vec3, Mat4, LVector2f, LVector3f


class P3dVec2:

    attr_lst = ['x', 'y']
    p3d_cls = Vec2

    def __init__(self, *args):
        self._vec = self.p3d_cls(*args)

    @property
    def x(self): return self._vec.x

    @property
    def y(self): return self._vec.y

    @property
    def xy(self): return P3dVec2(self._vec.x, self._vec.y)

    def signed_angle_deg(self, vec):
        return self._vec.signed_angle_deg(LVector2f(vec.x, vec.y))

    def dot(self, other):
        if isinstance(other, tuple): other = self.__class__(*other)
        return self._vec.dot(other._vec)
        #TODO: don't access a protected member

    def __neg__(self):
        nvec = - self._vec
        return self.__class__(*[getattr(nvec, attr) for attr in self.attr_lst])

    def __add__(self, vec):
        if isinstance(vec, tuple): vec = self.__class__(*vec)
        svec = self._vec + vec._vec  #TODO: don't access a protected member
        return self.__class__(*[getattr(svec, attr) for attr in self.attr_lst])

    def __sub__(self, vec):
        if isinstance(vec, tuple): vec = self.__class__(*vec)
        svec = self._vec - vec._vec  #TODO: don't access a protected member
        return self.__class__(*[getattr(svec, attr) for attr in self.attr_lst])

    def __mul__(self, val):
        svec = self._vec * val
        return self.__class__(*[getattr(svec, attr) for attr in self.attr_lst])

    def normalize(self):
        self._vec.normalize()
        return self.__class__(*self.attrs)

    @property
    def attrs(self): return [getattr(self._vec, fld) for fld in self.attr_lst]

    @property
    def normalized(self):
        vec = self.p3d_cls(*self.attrs)
        vec.normalize()
        return self.__class__(*[getattr(vec, fld) for fld in self.attr_lst])

    def rotate(self, deg):
        rot_mat = Mat4()
        rot_mat.set_rotate_mat(deg, (0, 0, 1))
        self._vec = rot_mat.xform_vec(self._vec)

    def length(self): return self._vec.length()

    def __repr__(self):
        tmpl = '%s(' + \
               ', '.join(['%s' for _ in range(len(self.attr_lst))]) + ')'
        rnd = lambda x: round(x, 3)
        vals = [rnd(getattr(self._vec, attr)) for attr in self.attr_lst]
        pars = tuple([self.__class__.__name__] + vals)
        return tmpl % pars


class P3dVec3(P3dVec2):

    attr_lst = ['x', 'y', 'z']
    p3d_cls = Vec3

    @property
    def z(self): return self._vec.z

    def signed_angle_deg(self, vec):
        v_up = LVector3f(0, 0, 1)
        return self._vec.signed_angle_deg(LVector3f(vec.x, vec.y, vec.z), v_up)
