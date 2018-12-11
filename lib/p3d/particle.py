from math import pi, sin, cos
from array import array
from random import uniform
from itertools import chain
from panda3d.core import GeomVertexArrayFormat, Geom, GeomVertexFormat, \
    GeomVertexData, GeomVertexWriter, GeomPoints, OmniBoundingVolume, \
    GeomNode, Vec3, ShaderAttrib, TexGenAttrib, TextureStage, Texture, \
    GeomEnums, NodePath
from yyagl.lib.p3d.shader import load_shader
from yyagl.lib.p3d.gfx import P3dNode
from yyagl.engine.vec import Vec
from yyagl.gameobject import GameObject
import sys


class P3dParticle(GameObject):

    _vdata = {}  # don't regenerate input structures

    def __init__(
            self, emitter, texture, npart, color=(1, 1, 1, 1), ampl=pi/6,
            ray=.5, rate=.0001, gravity=-.85, vel=3.8, part_lifetime=1.0,
            autodestroy=None):
        GameObject.__init__(self)
        self.__emitternode = None
        self.part_lifetime = part_lifetime
        if emitter.__class__ != P3dNode:  # emitter is a position
            self.__emitternode = P3dNode(NodePath('tmp'))
            self.__emitternode.set_pos(emitter)
            self.__emitternode.reparent_to(self.eng.gfx.root)
            emitter = self.__emitternode
        self.emitter = emitter
        #self._nodepath = parent.parent.attach_new_node(self.__node(texture, part_time, npart, color, ampl, ray, rate, gravity, vel))
        self._nodepath = render.attach_new_node(self.__node(texture, npart, color, ampl, ray, rate, gravity, vel))
        self._nodepath.set_transparency(True)
        self._nodepath.set_bin('fixed', 0)
        self.__set_shader(texture, color, gravity, part_lifetime)
        self._nodepath.set_render_mode_thickness(10)
        self._nodepath.set_tex_gen(TextureStage.getDefault(),
                                   TexGenAttrib.MPointSprite)
        self._nodepath.set_depth_write(False)
        self.upd_tsk = taskMgr.add(self._update, 'update')
        if autodestroy: self.eng.do_later(autodestroy, self.destroy)

    def __node(self, texture, npart, color, ampl, ray, rate, gravity, vel):
        prims = GeomPoints(GeomEnums.UH_static)
        prims.add_next_vertices(npart)
        geom = Geom(self.__vdata(texture, npart, color, ampl, ray, rate, gravity, vel))
        geom.add_primitive(prims)
        geom.set_bounds(OmniBoundingVolume())
        node = GeomNode('node')
        node.add_geom(geom)
        return node

    def __vdata(self, texture, npart, color, ampl, ray, rate, gravity, vel):
        if (texture, npart, color, ampl, ray, rate, gravity) in P3dParticle._vdata:
            vdata, pos, times, vels = P3dParticle._vdata[texture, npart, color, ampl, ray, rate, gravity]
            self.__set_textures(npart, pos, times, vels)
            return vdata
        pos, times, vels = self.__init_textures(npart, ray, rate, ampl, vel)
        self.__set_textures(npart, pos, times, vels)
        format_ = GeomVertexFormat.get_empty()
        vdata = GeomVertexData('abc', format_, GeomEnums.UH_static)
        P3dParticle._vdata[texture, npart, color, ampl, ray, rate, gravity] = vdata, pos, times, vels
        return P3dParticle._vdata[texture, npart, color, ampl, ray, rate, gravity][0]

    def __init_textures(self, npart, ray, rate, ampl, vel):
        positions = [self.__rnd_pos(ray) for i in range(npart)]
        pos_lst = [[pos.x, pos.y, pos.z, 1] for pos in positions]
        pos_lst = list(chain.from_iterable(pos_lst))
        start_times = [(rate * i, 0, 0, 0) for i in range(npart)]
        times_lst = list(chain.from_iterable(start_times))
        velocities = P3dParticle.__init_velocities(npart, ampl, vel)
        vel_lst = [[vel[0], vel[1], vel[2], 1] for vel in velocities]
        vel_lst = list(chain.from_iterable(vel_lst))
        return pos_lst, times_lst, vel_lst

    def __set_textures(self, npart, pos_lst, times_lst, vel_lst):
        self.tex_pos = self.__texture(pos_lst, 'start_positions', npart)
        self.tex_curr_pos = self.__texture(pos_lst, 'positions', npart)
        self.tex_times = self.__texture(times_lst, 'start_times', npart)
        self.tex_vel = self.__texture(vel_lst, 'start_velocities', npart)
        self.tex_curr_vel = self.__texture(vel_lst, 'velocities', npart)

    def __texture(self, lst, name, npart):
        data = array('f', lst)
        tex = Texture(name)
        tex.setup_buffer_texture(npart, Texture.T_float, Texture.F_rgba32, GeomEnums.UH_static)
        tex.set_ram_image(data.tostring() if sys.version_info[0] < 3 else data.tobytes())
        return tex

    def __rnd_pos(self, ray):
        ro = uniform(0, ray)
        alpha = uniform(0, 2 * pi)
        return Vec3(ro * cos(alpha), ro * sin(alpha), 0)

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

    def __set_shader(self, texture, color, gravity, part_lifetime):
        path = 'yyagl/assets/shaders/'
        shader = load_shader(path + 'particle.vert', path + 'particle.frag')
        if not shader: return
        self._nodepath.set_shader(shader)
        shader_attrib = ShaderAttrib.make(shader)
        shader_attrib = shader_attrib.set_flag(ShaderAttrib.F_shader_point_size, True)
        self._nodepath.set_attrib(shader_attrib)
        inputs = [
            ('start_time', globalClock.get_frame_time()),
            ('part_lifetime', part_lifetime),
            ('start_vel', self.tex_vel),
            ('curr_vel', self.tex_curr_vel),
            ('start_particle_time', self.tex_times),
            ('start_pos', self.tex_pos),
            ('curr_pos', self.tex_curr_pos),
            ('emitter_pos', self.emitter.get_pos(P3dNode(render))),
            ('delta_t', 0),
            ('emitting', 1),
            ('col', color),
            ('gravity', gravity),
            ('tex_in', loader.loadTexture('yyagl/assets/images/%s.txo' % texture))]
        map(lambda inp: self._nodepath.set_shader_input(*inp), inputs)

    def _update(self, task):
        if self.emitter and not self.emitter.is_empty:
            pos = self.emitter.get_pos(P3dNode(render))
        else: pos = (0, 0, 0)
        self._nodepath.set_shader_input('emitter_pos', pos)
        self._nodepath.set_shader_input('delta_t', globalClock.get_dt())
        return task.again

    def destroy(self, now=False):
        self._nodepath.set_shader_input('emitting', 0)
        self.eng.do_later(0 if now else self.part_lifetime, self.__destroy)

    def __destroy(self):
        self.upd_tsk = taskMgr.remove(self.upd_tsk)
        self._nodepath = self._nodepath.remove_node()
        if self.__emitternode: self.__emitternode = self.__emitternode.destroy()
        GameObject.destroy(self)
