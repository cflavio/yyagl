from math import pi, sin, cos
from random import uniform
from panda3d.core import GeomVertexArrayFormat, Geom, GeomVertexFormat, \
    GeomVertexData, GeomVertexWriter, GeomPoints, OmniBoundingVolume, \
    GeomNode, Shader, Vec3
from ..gameobject import GameObject


vert = '''#version 130
in vec3 init_vel;
in vec3 start_particle_time;
uniform float osg_FrameTime;
uniform float start_time;
uniform mat4 p3d_ModelViewProjectionMatrix;
out float time;

void main() {
    vec3 gravity = vec3(.0, .0, -.85);
    time = osg_FrameTime - start_time;
    vec3 pos = vec3(0);
    if (time > start_particle_time.x) {
        float t = time - start_particle_time.x;
        pos = init_vel * t + gravity * t * t;
    }
    gl_Position = p3d_ModelViewProjectionMatrix * vec4(pos, 1.0);
}'''


frag = '''#version 130
in float time;
uniform float tot_time;
uniform vec4 color;
void main() {
    gl_FragColor = vec4(color.rgb, clamp(1 - time / tot_time, 0, 1));
}'''


class Particle(GameObject):

    num_particles = 10000
    rate = .0001
    _buffered_vel = []
    _buffered_rates = []

    def __init__(self, parent, pos, hpr, color, tot_time):
        GameObject.__init__(self)
        self.__set_nodepath(parent, pos, hpr)
        self.__set_shader(color, tot_time)
        self.destroy_tsk = self.eng.do_later(tot_time, self.destroy)

    def __set_nodepath(self, parent, pos, hpr):
        array = GeomVertexArrayFormat()
        array.add_column('init_vel', 3, Geom.NTFloat32, Geom.CPoint)
        array.add_column('start_particle_time', 3, Geom.NTFloat32, Geom.CPoint)
        format = GeomVertexFormat()
        format.add_array(array)
        format = GeomVertexFormat.register_format(format)
        vdata = GeomVertexData('info', format, Geom.UHStatic)
        vdata.set_num_rows(1)
        vertex = GeomVertexWriter(vdata, 'init_vel')
        map(lambda vtx: vertex.add_data3f(*vtx), self.__init_velocities())
        start_time = GeomVertexWriter(vdata, 'start_particle_time')
        map(lambda vtx: start_time.add_data3f(*vtx), self.__init_rates())
        prim = GeomPoints(Geom.UH_static)
        prim.add_next_vertices(self.num_particles)
        geom = Geom(vdata)
        geom.add_primitive(prim)
        geom.set_bounds(OmniBoundingVolume())
        node = GeomNode('gnode')
        node.add_geom(geom)
        self.__np = parent.attach_new_node(node)
        self.__np.set_transparency(True)
        self.__np.setBin('fixed', 0)
        self.__np.set_pos(pos)
        self.__np.set_hpr(hpr)

    def __set_shader(self, color, tot_time):
        self.__np.set_shader(Shader.make(Shader.SL_GLSL, vert, frag))
        self.__np.set_shader_input('color', color)
        self.__np.set_shader_input('start_time', globalClock.get_frame_time())
        self.__np.set_shader_input('tot_time', tot_time)

    def __init_velocities(self):
        if not self._buffered_vel:
            for i in range(self.num_particles):
                theta = uniform(0, pi / 6)
                phi = uniform(0, 2 * pi)
                v = Vec3(
                    sin(theta) * cos(phi),
                    sin(theta) * sin(phi),
                    cos(theta))
                velocity = uniform(3.25, 4.5)
                v = v * velocity
                self._buffered_vel += [(v.x, v.y, v.z)]
        return self._buffered_vel

    def __init_rates(self):
        if not self._buffered_rates:
            self._buffered_rates = [
                (self.rate * i, 0, 0) for i in range(self.num_particles)]
        return self._buffered_rates

    def destroy(self):
        self.destroy_tsk = self.eng.remove_do_later(self.destroy_tsk)
        self.__np = self.__np.remove_node()
        GameObject.destroy(self)
