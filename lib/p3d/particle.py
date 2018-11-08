from math import pi, sin, cos
from random import uniform
from panda3d.core import GeomVertexArrayFormat, Geom, GeomVertexFormat, \
    GeomVertexData, GeomVertexWriter, GeomPoints, OmniBoundingVolume, \
    GeomNode, Vec3, ShaderAttrib, TexGenAttrib, TextureStage
from yyagl.lib.p3d.shader import load_shader
from yyagl.engine.vec import Vec


class P3dParticle(object):

    num_particles = 10000
    rate = .0001  # generation rate
    _vdata = None  # don't regenerate input structures

    def __init__(self, parent, pos, hpr, color, tot_time):
        self._nodepath = parent.attach_node(self.__node())
        self._nodepath.set_transparency(True)
        self._nodepath.node.set_bin('fixed', 0)
        self._nodepath.set_pos(Vec(pos.x, pos.y, pos.z))
        self._nodepath.set_hpr(hpr)
        self.__set_shader(color, tot_time)
        self._nodepath.node.set_render_mode_thickness(10)
        self._nodepath.node.set_tex_gen(TextureStage.getDefault(),
                                        TexGenAttrib.MPointSprite)
        self._nodepath.node.set_depth_write(False)

    def __node(self):
        prim = GeomPoints(Geom.UH_static)
        prim.add_next_vertices(P3dParticle.num_particles)
        geom = Geom(self.__vdata())
        geom.add_primitive(prim)
        geom.set_bounds(OmniBoundingVolume())
        node = GeomNode('gnode')
        node.add_geom(geom)
        return node

    def __vdata(self):
        if P3dParticle._vdata: return P3dParticle._vdata
        # TODO: use python buffer protocol in place of this
        vdata = GeomVertexData('info', self.__format(), Geom.UHStatic)
        vdata.set_num_rows(1)
        vertex = GeomVertexWriter(vdata, 'init_vel')
        vels = P3dParticle.__init_velocities()
        map(lambda vtx: vertex.add_data3f(*vtx), vels)
        start_time = GeomVertexWriter(vdata, 'start_particle_time')
        npart = P3dParticle.num_particles
        rates = [(P3dParticle.rate * i, 0, 0) for i in range(npart)]
        map(lambda vtx: start_time.add_data3f(*vtx), rates)
        P3dParticle._vdata = vdata
        return P3dParticle._vdata

    def __format(self):
        array = GeomVertexArrayFormat()
        array.add_column('init_vel', 3, Geom.NTFloat32, Geom.CPoint)
        array.add_column('start_particle_time', 3, Geom.NTFloat32, Geom.CPoint)
        _format = GeomVertexFormat()
        _format.add_array(array)
        return GeomVertexFormat.register_format(_format)

    @staticmethod
    def __init_velocities():
        vels = []
        for _ in range(P3dParticle.num_particles):
            vec = P3dParticle.__set_vel()
            vels += [(vec.x, vec.y, vec.z)]
        return vels

    @staticmethod
    def __set_vel():
            theta = uniform(0, pi / 6)
            phi = uniform(0, 2 * pi)
            vec = Vec3(
                sin(theta) * cos(phi),
                sin(theta) * sin(phi),
                cos(theta))
            velocity = uniform(3.25, 4.5)
            return vec * velocity

    def __set_shader(self, color, tot_time):
        path = 'yyagl/assets/shaders/'
        shader = load_shader(path + 'particle.vert', path + 'particle.frag')
        if not shader: return
        self._nodepath.node.set_shader(shader)
        shader_attrib = ShaderAttrib.make(shader)
        shader_attrib = shader_attrib.set_flag(ShaderAttrib.F_shader_point_size, True)
        self._nodepath.node.set_attrib(shader_attrib)
        inputs = [('color', color),
                  ('start_time', globalClock.get_frame_time()),
                  ('tot_time', tot_time),
                  ('tex_in', loader.loadTexture('yyagl/assets/images/sparkle.png'))]
        map(lambda inp: self._nodepath.node.set_shader_input(*inp), inputs)

    def destroy(self):
        self._nodepath = self._nodepath.node.remove_node()
