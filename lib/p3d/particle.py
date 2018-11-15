from math import pi, sin, cos
from random import uniform
from panda3d.core import GeomVertexArrayFormat, Geom, GeomVertexFormat, \
    GeomVertexData, GeomVertexWriter, GeomPoints, OmniBoundingVolume, \
    GeomNode, Vec3, ShaderAttrib, TexGenAttrib, TextureStage
from yyagl.lib.p3d.shader import load_shader
from yyagl.engine.vec import Vec


class P3dParticle(object):

    _vdata = {}  # don't regenerate input structures

    def __init__(
            self, parent, pos, hpr, texture, part_time, npart,
            color=(1, 1, 1, 1), ampl=pi/6, ray=.5, rate=.0001, gravity=-.85, vel=3.8):
        self._nodepath = parent.attach_node(self.__node(texture, part_time, npart, color, ampl, ray, rate, gravity, vel))
        self._nodepath.set_transparency(True)
        self._nodepath.node.set_bin('fixed', 0)
        self._nodepath.set_pos(Vec(pos.x, pos.y, pos.z))
        self._nodepath.set_hpr(hpr)
        self.__set_shader(texture, part_time, color, gravity)
        self._nodepath.node.set_render_mode_thickness(10)
        self._nodepath.node.set_tex_gen(TextureStage.getDefault(),
                                        TexGenAttrib.MPointSprite)
        self._nodepath.node.set_depth_write(False)

    def __node(self, texture, part_time, npart, color, ampl, ray, rate, gravity, vel):
        prim = GeomPoints(Geom.UH_static)
        prim.add_next_vertices(npart)
        geom = Geom(self.__vdata(texture, part_time, npart, color, ampl, ray, rate, gravity, vel))
        geom.add_primitive(prim)
        geom.set_bounds(OmniBoundingVolume())
        node = GeomNode('gnode')
        node.add_geom(geom)
        return node

    def __vdata(self, texture, part_time, npart, color, ampl, ray, rate, gravity, vel):
        if (texture, part_time, npart, color, ampl, ray, rate, gravity) in P3dParticle._vdata:
            return P3dParticle._vdata[texture, part_time, npart, color, ampl, ray, rate, gravity]
        # TODO: use python buffer protocol in place of this
        vdata = GeomVertexData('info', self.__format(), Geom.UHStatic)
        vdata.set_num_rows(1)
        vertex = GeomVertexWriter(vdata, 'init_vel')
        vels = P3dParticle.__init_velocities(npart, ampl, vel)
        map(lambda vtx: vertex.add_data3f(*vtx), vels)
        start_time = GeomVertexWriter(vdata, 'start_particle_time')
        rates = [(rate * i, 0, 0) for i in range(npart)]
        map(lambda vtx: start_time.add_data3f(*vtx), rates)
        start_pos = GeomVertexWriter(vdata, 'start_pos')
        positions = [self.__rnd_pos(ray) for i in range(npart)]
        map(lambda vtx: start_pos.add_data3f(*vtx), positions)
        P3dParticle._vdata[texture, part_time, npart, color, ampl, ray, rate, gravity] = vdata
        return P3dParticle._vdata[texture, part_time, npart, color, ampl, ray, rate, gravity]

    def __rnd_pos(self, ray):
        ro = uniform(0, ray)
        alpha = uniform(0, 2 * pi)
        return Vec3(ro * cos(alpha), ro * sin(alpha), 0)

    def __format(self):
        array = GeomVertexArrayFormat()
        array.add_column('init_vel', 3, Geom.NTFloat32, Geom.CPoint)
        array.add_column('start_particle_time', 3, Geom.NTFloat32, Geom.CPoint)
        array.add_column('start_pos', 3, Geom.NTFloat32, Geom.CPoint)
        _format = GeomVertexFormat()
        _format.add_array(array)
        return GeomVertexFormat.register_format(_format)

    @staticmethod
    def __init_velocities(npart, ampl, vel):
        vels = []
        for _ in range(npart):
            vec = P3dParticle.__set_vel(ampl, vel)
            vels += [(vec.x, vec.y, vec.z)]
        return vels

    @staticmethod
    def __set_vel(ampl, vel):
        theta = uniform(0, ampl)
        phi = uniform(0, 2 * pi)
        vec = Vec3(
            sin(theta) * cos(phi),
            sin(theta) * sin(phi),
            cos(theta))
        return vec * uniform(vel * .8, vel * 1.2)

    def __set_shader(self, texture, part_time, color, gravity):
        path = 'yyagl/assets/shaders/'
        shader = load_shader(path + 'particle.vert', path + 'particle.frag')
        if not shader: return
        self._nodepath.node.set_shader(shader)
        shader_attrib = ShaderAttrib.make(shader)
        shader_attrib = shader_attrib.set_flag(ShaderAttrib.F_shader_point_size, True)
        self._nodepath.node.set_attrib(shader_attrib)
        inputs = [('start_time', globalClock.get_frame_time()),
                  ('part_time', part_time),
                  ('col', color),
                  ('gravity', gravity),
                  ('tex_in', loader.loadTexture('yyagl/assets/images/%s.png' % texture))]
        map(lambda inp: self._nodepath.node.set_shader_input(*inp), inputs)

    def destroy(self):
        self._nodepath = self._nodepath.node.remove_node()
