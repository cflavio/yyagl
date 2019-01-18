from math import pi, sin, cos
from array import array
from random import uniform
from itertools import chain
from panda3d.core import (Geom, GeomVertexFormat, GeomVertexData, GeomPoints,
    OmniBoundingVolume, GeomNode, Vec3, ShaderAttrib, TexGenAttrib,
    TextureStage, Texture, GeomEnums, NodePath)
from yyagl.lib.p3d.shader import load_shader
from yyagl.lib.p3d.gfx import P3dNode
from yyagl.gameobject import GameObject
import sys


class P3dParticle(GameObject):

    _vdata = {}  # don't regenerate input structures

    def __init__(
            self, emitter, texture, color=(1, 1, 1, 1), ampl=pi/6,
            ray=.5, rate=.001, gravity=-9.81, vel=1.0, part_duration=1.0,
            autodestroy=None):
        GameObject.__init__(self)
        if not self.eng.lib.version.startswith('1.10'): return
        self.__tex_pos = self.__tex_curr_pos = self.__tex_times = \
            self.__tex_start_vel = self.__tex_curr_vel = self.__emitternode = \
            None
        self.__texture = texture
        self.__color = color
        self.__ampl = ampl
        self.__ray = ray
        self.__rate = rate
        self.__gravity = gravity
        self.__vel = vel
        self.__part_duration = part_duration
        self.__npart = int(round(part_duration * 1 / rate))
        if emitter.__class__ != P3dNode:  # emitter is a position
            self.__emitternode = P3dNode(NodePath('tmp'))
            self.__emitternode.set_pos(emitter)
            self.__emitternode.reparent_to(self.eng.gfx.root)
            emitter = self.__emitternode
        self.__emitter = emitter
        self.__old_pos = (0, 0, 0)
        self._nodepath = render.attach_new_node(self.__node())
        self._nodepath.set_transparency(True)
        self._nodepath.set_bin('fixed', 0)
        self.__set_shader()
        self._nodepath.set_render_mode_thickness(10)
        self._nodepath.set_tex_gen(TextureStage.getDefault(),
                                   TexGenAttrib.MPointSprite)
        self._nodepath.set_depth_write(False)
        self.upd_tsk = taskMgr.add(self._update, 'update')
        if autodestroy: self.eng.do_later(autodestroy, self.destroy)

    def __node(self):
        points = GeomPoints(GeomEnums.UH_static)
        points.add_next_vertices(self.__npart)
        geom = Geom(self.__vdata())
        geom.add_primitive(points)
        geom.set_bounds(OmniBoundingVolume())
        node = GeomNode('node')
        node.add_geom(geom)
        return node

    def __vdata(self):
        if (self.__texture, self.__npart, self.__color, self.__ampl, self.__ray,
            self.__rate, self.__gravity) in P3dParticle._vdata:
            vdata, pos, times, vels = P3dParticle._vdata[
                self.__texture, self.__npart, self.__color, self.__ampl,
                self.__ray, self.__rate, self.__gravity]
            self.__set_textures(pos, times, vels)
            return vdata
        pos, times, vels = self.__init_textures()
        self.__set_textures(pos, times, vels)
        format_ = GeomVertexFormat.get_empty()
        vdata = GeomVertexData('abc', format_, GeomEnums.UH_static)
        P3dParticle._vdata[self.__texture, self.__npart, self.__color,
                           self.__ampl, self.__ray, self.__rate,
                           self.__gravity] = \
            vdata, pos, times, vels
        return P3dParticle._vdata[self.__texture, self.__npart, self.__color,
                                  self.__ampl, self.__ray, self.__rate,
                                  self.__gravity][0]

    def __init_textures(self):
        positions = [self.__rnd_pos() for i in range(self.__npart)]
        pos_lst = [[pos.x, pos.y, pos.z, 1] for pos in positions]
        pos_lst = list(chain.from_iterable(pos_lst))
        emission_times = [(self.__rate * i, 0, 0, 0) for i in range(self.__npart)]
        times_lst = list(chain.from_iterable(emission_times))
        velocities = self.__init_velocities()
        vel_lst = [[v_vel[0], v_vel[1], v_vel[2], 1] for v_vel in velocities]
        vel_lst = list(chain.from_iterable(vel_lst))
        return pos_lst, times_lst, vel_lst

    def __set_textures(self, pos_lst, times_lst, vel_lst):
        self.__tex_pos = self.__buff_tex(pos_lst)
        self.__tex_curr_pos = self.__buff_tex(pos_lst)
        self.__tex_times = self.__buff_tex(times_lst)
        self.__tex_start_vel = self.__buff_tex(vel_lst)
        self.__tex_curr_vel = self.__buff_tex(vel_lst)

    def __buff_tex(self, vals):
        data = array('f', vals)
        tex = Texture('tex')
        tex.setup_buffer_texture(
            self.__npart, Texture.T_float, Texture.F_rgba32, GeomEnums.UH_static)
        conv_mth = 'tostring' if sys.version_info[0] < 3 else 'tobytes'
        tex.set_ram_image(getattr(data, conv_mth)())
        return tex

    def __rnd_pos(self):
        ro = uniform(0, self.__ray)
        alpha = uniform(0, 2 * pi)
        return Vec3(ro * cos(alpha), ro * sin(alpha), 0)

    def __init_velocities(self):
        vels = []
        for _ in range(self.__npart):
            vec = self.__rnd_vel()
            vels += [(vec.x, vec.y, vec.z)]
        return vels

    def __rnd_vel(self):
        theta = uniform(0, self.__ampl)
        phi = uniform(0, 2 * pi)
        vec = Vec3(
            sin(theta) * cos(phi),
            sin(theta) * sin(phi),
            cos(theta))
        return vec * uniform(self.__vel * .8, self.__vel * 1.2)

    def __set_shader(self):
        path = 'yyagl/assets/shaders/'
        shader = load_shader(path + 'particle.vert', path + 'particle.frag')
        if not shader: return
        self._nodepath.set_shader(shader)
        sha_attr = ShaderAttrib.make(shader)
        sha_attr = sha_attr.set_flag(ShaderAttrib.F_shader_point_size, True)
        self._nodepath.set_attrib(sha_attr)
        img = loader.loadTexture('yyagl/assets/images/%s.txo' % self.__texture)
        inputs = [
            ('start_pos', self.__tex_pos),
            ('positions', self.__tex_curr_pos),
            ('emitter_old_pos', self.__old_pos),
            ('emitter_pos', self.__emitter.get_pos(P3dNode(render))),
            ('start_vel', self.__tex_start_vel),
            ('velocities', self.__tex_curr_vel),
            ('accel', (0, 0, self.__gravity)),
            ('start_time', globalClock.get_frame_time()),
            ('emission_times', self.__tex_times),
            ('part_duration', self.__part_duration),
            ('delta_t', 0),
            ('emitting', 1),
            ('col', self.__color),
            ('image', img)
            ]
        map(lambda inp: self._nodepath.set_shader_input(*inp), inputs)

    def _update(self, task):
        if self.__emitter and not self.__emitter.is_empty:
            pos = self.__emitter.get_pos(P3dNode(render))
        else: pos = (0, 0, 0)
        self._nodepath.set_shader_input('emitter_old_pos', self.__old_pos)
        self._nodepath.set_shader_input('emitter_pos', pos)
        self._nodepath.set_shader_input('delta_t', globalClock.get_dt())
        self.__old_pos = pos
        return task.again

    def destroy(self, now=False):
        self._nodepath.set_shader_input('emitting', 0)
        self.eng.do_later(0 if now else 1.2 * self.__part_duration, self.__destroy)

    def __destroy(self):
        self.upd_tsk = taskMgr.remove(self.upd_tsk)
        self._nodepath = self._nodepath.remove_node()
        if self.__emitternode:
            self.__emitternode = self.__emitternode.destroy()
        GameObject.destroy(self)
