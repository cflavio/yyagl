from panda3d.core import GeomVertexData, GeomVertexWriter, GeomVertexFormat, \
    Geom, GeomTriangles, GeomNode, Mat4, Material, OmniBoundingVolume, Shader
from direct.interval.MetaInterval import Sequence
from direct.interval.FunctionInterval import Wait, Func
from direct.interval.LerpInterval import LerpFunc
from yyagl.gameobject import GameObject


vert = '''
#version 120
attribute vec4 p3d_Vertex;
attribute vec2 p3d_MultiTexCoord0;
uniform mat4 p3d_ModelViewProjectionMatrix;

void main() {
    gl_Position = p3d_ModelViewProjectionMatrix * p3d_Vertex;
}'''

frag = '''
#version 120
uniform float alpha;

void main() {
    gl_FragColor = vec4(.35, .35, .35, alpha);
}'''


class Skidmark(GameObject):

    def __init__(self, whl_pos, whl_radius, car_h):
        GameObject.__init__(self)
        self.radius = whl_radius
        v_f = GeomVertexFormat.getV3()
        vdata = GeomVertexData('skid', v_f, Geom.UHDynamic)
        prim = GeomTriangles(Geom.UHStatic)
        self.vtx_cnt = 1
        self.last_pos = whl_pos
        geom = Geom(vdata)
        geom.add_primitive(prim)
        self.node = GeomNode('gnode')
        self.node.add_geom(geom)
        nodepath = self.eng.gfx.root.attach_node(self.node)
        nodepath.set_transparency(True)
        nodepath.set_depth_offset(1)
        nodepath.node.set_two_sided(True)  # for self-shadowing issues
        self.__set_material(nodepath)
        nodepath.p3dnode.set_bounds(OmniBoundingVolume())
        self.add_vertices(whl_radius, car_h)
        self.add_vertices(whl_radius, car_h)

        def alpha(time, n_p):
            if not n_p.is_empty:
                n_p.node.set_shader_input('alpha', time)
            # this if seems necessary since, if there are skidmarks and you
            # exit from the race (e.g. back to the menu), then alpha is being
            # called from the interval manager even if the interval manager
            # correctly says that there are 0 intervals.
        self.remove_seq = Sequence(
            Wait(8),
            LerpFunc(alpha, 8, .5, 0, 'easeInOut', [nodepath]),
            Func(nodepath.remove_node))
        self.remove_seq.start()

    @staticmethod
    def __set_material(nodepath):
        #mat = Material()
        #mat.set_ambient((.35, .35, .35, .5))
        #mat.set_diffuse((.35, .35, .35, .5))
        #mat.set_specular((.35, .35, .35, .5))
        #mat.set_shininess(12.5)
        #nodepath.set_material(mat)
        nodepath.node.set_shader(Shader.make(Shader.SL_GLSL, vert, frag))
        nodepath.node.set_shader_input('alpha', .5)

    def add_vertices(self, whl_radius, car_h):
        base_pos = self.last_pos + (0, 0, -whl_radius + .05)
        rot_mat = Mat4()
        rot_mat.set_rotate_mat(car_h, (0, 0, 1))
        vdata = self.node.modify_geom(0).modify_vertex_data()
        vwriter = GeomVertexWriter(vdata, 'vertex')
        vwriter.set_row(vdata.get_num_rows())
        vwriter.add_data3f(base_pos + rot_mat.xform_vec((-.12, 0, 0)))
        vwriter.add_data3f(base_pos + rot_mat.xform_vec((.12, 0, 0)))
        cnt = self.vtx_cnt
        prim = self.node.modify_geom(0).modify_primitive(0)
        if cnt >= 3:
            prim.add_vertices(cnt - 3, cnt - 2, cnt - 1)
            prim.add_vertices(cnt - 2, cnt, cnt - 1)
        self.vtx_cnt += 2

    def update(self, whl_pos, car_h):
        if (whl_pos - self.last_pos).length() > .2:
            self.last_pos = whl_pos
            self.add_vertices(self.radius, car_h)

    def destroy(self):
        self.remove_seq = self.remove_seq.finish()
        GameObject.destroy(self)
