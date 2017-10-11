from math import pi, sin, cos
from random import uniform
from panda3d.core import GeomVertexArrayFormat, Geom, GeomVertexFormat, \
    GeomVertexData, GeomVertexWriter, GeomPoints, OmniBoundingVolume, \
    GeomNode, Shader, Vec3


class PandaParticle(object):

    num_particles = 10000
    rate = .0001  # generation rate
    _vdata = None  # don't regenerate input structures

    @staticmethod
    def set_nodepath(parent, pos, hpr):
        array = GeomVertexArrayFormat()
        array.add_column('init_vel', 3, Geom.NTFloat32, Geom.CPoint)
        array.add_column('start_particle_time', 3, Geom.NTFloat32, Geom.CPoint)
        _format = GeomVertexFormat()
        _format.add_array(array)
        _format = GeomVertexFormat.register_format(_format)
        if not PandaParticle._vdata:  #TODO: use python buffer protocol in place of this
            vdata = GeomVertexData('info', _format, Geom.UHStatic)
            vdata.set_num_rows(1)
            vertex = GeomVertexWriter(vdata, 'init_vel')
            map(lambda vtx: vertex.add_data3f(*vtx), PandaParticle.__init_velocities())
            start_time = GeomVertexWriter(vdata, 'start_particle_time')
            rates = [(PandaParticle.rate * i, 0, 0) for i in range(PandaParticle.num_particles)]
            map(lambda vtx: start_time.add_data3f(*vtx), rates)
            PandaParticle._vdata = vdata
        vdata = PandaParticle._vdata
        prim = GeomPoints(Geom.UH_static)
        prim.add_next_vertices(PandaParticle.num_particles)
        geom = Geom(vdata)
        geom.add_primitive(prim)
        geom.set_bounds(OmniBoundingVolume())
        node = GeomNode('gnode')
        node.add_geom(geom)
        __np = parent.attach_node(node)
        __np.set_transparency(True)
        __np.node.set_bin('fixed', 0)
        __np.set_pos(pos)
        __np.set_hpr(hpr)
        return __np

    @staticmethod
    def __init_velocities():
        vels = []
        for _ in range(PandaParticle.num_particles):
            theta = uniform(0, pi / 6)
            phi = uniform(0, 2 * pi)
            vec = Vec3(
                sin(theta) * cos(phi),
                sin(theta) * sin(phi),
                cos(theta))
            velocity = uniform(3.25, 4.5)
            vec = vec * velocity
            vels += [(vec.x, vec.y, vec.z)]
        return vels

    @staticmethod
    def set_shader(np, color, tot_time):
        np.node.set_shader(Shader.load(Shader.SL_GLSL, 'yyagl/assets/shaders/particle.vert', 'yyagl/assets/shaders/particle.frag'))
        np.node.set_shader_input('color', color)
        np.node.set_shader_input('start_time', globalClock.get_frame_time())
        np.node.set_shader_input('tot_time', tot_time)
