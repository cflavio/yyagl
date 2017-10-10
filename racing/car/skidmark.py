from panda3d.core import GeomVertexData, GeomVertexWriter, GeomVertexFormat, \
    Geom, GeomTriangles, GeomNode, Mat4, Material, OmniBoundingVolume
from direct.interval.MetaInterval import Sequence
from direct.interval.FunctionInterval import Wait, Func
from direct.interval.LerpInterval import LerpFunc
from yyagl.gameobject import GameObject


class Skidmark(GameObject):

    def __init__(self, whl_pos, whl_radius, car_h):
        GameObject.__init__(self)
        self.radius = whl_radius
        v_f = GeomVertexFormat.getV3()
        self.vdata = GeomVertexData('skid', v_f, Geom.UHDynamic)
        self.vdata.set_num_rows(1)
        self.vwriter = GeomVertexWriter(self.vdata, 'vertex')
        self.prim = GeomTriangles(Geom.UHStatic)
        self.vtx_cnt = 1
        self.last_pos = whl_pos
        geom = Geom(self.vdata)
        geom.add_primitive(self.prim)
        node = GeomNode('gnode')
        node.add_geom(geom)
        nodepath = self.eng.gfx.root.attach_node(node)
        nodepath.set_transparency(True)
        nodepath.set_depth_offset(1)
        self.__set_material(nodepath)
        nodepath.get_node().set_bounds(OmniBoundingVolume())
        self.add_vertices(whl_radius, car_h)
        self.add_vertices(whl_radius, car_h)

        def alpha(time, n_p):
            if not n_p.is_empty():
                n_p.set_alpha_scale(time)
            # this if seems necessary since, if there are skidmarks and you
            # exit from the race (e.g. back to the menu), then alpha is being
            # called from the interval manager even if the interval manager
            # correctly says that there are 0 intervals.
        self.remove_seq = Sequence(
            Wait(8),
            LerpFunc(alpha, 8, 1, 0, 'easeInOut', [nodepath]),
            Func(nodepath.remove_node))
        self.remove_seq.start()

    @staticmethod
    def __set_material(nodepath):
        mat = Material()
        mat.set_ambient((.35, .35, .35, .5))
        mat.set_diffuse((.35, .35, .35, .5))
        mat.set_specular((.35, .35, .35, .5))
        mat.set_shininess(12.5)
        nodepath.set_material(mat)

    def add_vertices(self, whl_radius, car_h):
        base_pos = self.last_pos + (0, 0, -whl_radius + .05)
        rot_mat = Mat4()
        rot_mat.set_rotate_mat(car_h, (0, 0, 1))
        self.vwriter.add_data3f(base_pos + rot_mat.xform_vec((-.12, 0, 0)))
        self.vwriter.add_data3f(base_pos + rot_mat.xform_vec((.12, 0, 0)))
        cnt = self.vtx_cnt
        if cnt >= 3:
            self.prim.add_vertices(cnt - 3, cnt - 2, cnt - 1)
            self.prim.add_vertices(cnt - 2, cnt, cnt - 1)
        self.vtx_cnt += 2

    def update(self, whl_pos, car_h):
        if (whl_pos - self.last_pos).length() > .2:
            self.last_pos = whl_pos
            self.add_vertices(self.radius, car_h)

    def destroy(self):
        self.remove_seq = self.remove_seq.finish()
        GameObject.destroy(self)
