from os.path import exists, dirname
from panda3d.core import (get_model_path, AntialiasAttrib, PandaNode,
    LightRampAttrib, Camera, OrthographicLens, NodePath, OmniBoundingVolume,
                          AmbientLight as P3DAmbientLight, Spotlight as P3DSpotlight, Point2, Point3, Texture)
from direct.filter.CommonFilters import CommonFilters
from direct.actor.Actor import Actor
from yyagl.lib.p3d.p3d import LibP3d
from yyagl.facade import Facade
import datetime


class RenderToTexture(object):

    def __init__(self, size=(256, 256)):
        self.__set_buffer(size)
        self.__set_display_region()
        self.__set_camera()
        self.__set_root()
        self.display_region.set_camera(self.camera)

    def __set_buffer(self, size):
        self.buffer = base.win.make_texture_buffer('result buffer', size[0],
                                                   size[1])
        self.buffer.set_sort(-100)

    def __set_display_region(self):
        self.display_region = self.buffer.make_display_region()
        self.display_region.set_sort(20)

    def __set_camera(self):
        self.camera = NodePath(Camera('camera 2d'))
        lens = OrthographicLens()
        lens.set_film_size(1, 1)
        lens.set_near_far(-1000, 1000)
        self.camera.node().set_lens(lens)

    def __set_root(self):
        self.root = NodePath('root')
        self.root.set_depth_test(False)
        self.root.set_depth_write(False)
        self.camera.reparent_to(self.root)

    @property
    def texture(self): return self.buffer.get_texture()

    def destroy(self):
        base.graphicsEngine.remove_window(self.buffer)
        if base.win:  # if you close the window during a race
            base.win.remove_display_region(self.display_region)
        list(map(lambda node: node.remove_node(), [self.camera, self.root]))


class P3dGfxMgr(object):

    def __init__(self, model_path, antialiasing, shaders, srgb):
        self.root = P3dNode(render)
        self.__srgb = srgb
        self.callbacks = {}
        self.filters = None
        get_model_path().append_directory(model_path)
        if LibP3d.runtime():
            root_dir = LibP3d.p3dpath(dirname(__file__))
            paths = [root_dir + '/' + model_path, root_dir]
            list(map(get_model_path().append_directory, paths))
        render.set_shader_auto()
        render.set_two_sided(True)
        if antialiasing: render.set_antialias(AntialiasAttrib.MAuto)
        if shaders and base.win:
            self.filters = CommonFilters(base.win, base.cam)

    def load_model(self, filename, callback=None, anim=None):
        ext = '.bam' if exists(filename + '.bam') else ''
        if anim:
            anim_dct = {'anim': filename + '-Anim' + ext}
            return P3dNode(self.set_srgb(Actor(filename + ext, anim_dct)))
        elif callback:
            callb = lambda model: callback(P3dNode(self.set_srgb(model)))
            return loader.loadModel(filename + ext, callback=callb)
        else:
            return P3dNode(self.set_srgb(loader.loadModel(LibP3d.p3dpath(filename + ext))))

    def set_srgb(self, model):
        if self.__srgb:
            for texture in model.find_all_textures():
                texture.set_format(Texture.F_srgb)
        return model

    def toggle_aa(self, val=None):
        if render.has_antialias() and render.get_antialias() != AntialiasAttrib.MNone:
            render.clear_antialias()
        else: render.set_antialias(AntialiasAttrib.MAuto, 1)

    def set_toon(self):
        tmp_node = NodePath(PandaNode('temp node'))
        tmp_node.set_attrib(LightRampAttrib.make_single_threshold(.5, .4))
        tmp_node.set_shader_auto()
        base.cam.node().set_initial_state(tmp_node.get_state())
        self.filters.set_cartoon_ink(separation=1)

    def set_bloom(self):
        if not base.win: return
        self.filters.setBloom(
            blend=(.3, .4, .3, 0), mintrigger=.6, maxtrigger=1.0, desat=.6,
            intensity=1.0, size='medium')
        # default: (.3, .4, .3, 0), .6, 1, .6, 1, 'medium'

    @staticmethod
    def pos2d(node):
        p3d = base.cam.get_relative_point(node.node, Point3(0, 0, 0))
        p2d = Point2()
        return p2d if base.camLens.project(p3d, p2d) else None

    @property
    def shader_support(self):
        return base.win.get_gsg().get_supports_basic_shaders()

    def screenshot(self):
        time = datetime.datetime.now().strftime('%y%m%d%H%M%S')
        base.win.save_screenshot("yorg%s.jpg" % time)

    @staticmethod
    def enable_shader(): render.set_shader_auto()

    @staticmethod
    def disable_shader(): render.set_shader_off()

    @staticmethod
    def print_stats():
        info = [('render2d.analyze', base.render2d.analyze),
                ('render.analyze', base.render.analyze),
                ('render2d.ls', base.render2d.ls),
                ('render.ls', base.render.ls)]
        for elm in info:
            print('\n\n#####\n%s()' % elm[0])
            elm[1]()


class P3dNode:

    def __init__(self, nodepath):
        self.nodepath = nodepath
        self.node.set_python_tag('yyaglnode', self)

    def set_collide_mask(self, mask): return self.node.set_collide_mask(mask)
    def set_x(self, val): return self.node.set_x(val)
    def set_y(self, val): return self.node.set_y(val)
    def set_z(self, val): return self.node.set_z(val)
    def set_hpr(self, val): return self.node.set_hpr(val)
    def set_h(self, val): return self.node.set_h(val)
    def set_p(self, val): return self.node.set_p(val)
    def set_r(self, val): return self.node.set_r(val)
    def set_scale(self, val): return self.node.set_scale(val)
    def set_transparency(self, val): return self.node.set_transparency(val)
    def set_alpha_scale(self, val): return self.node.set_alpha_scale(val)
    def set_texture(self, ts, texture): return self.node.set_texture(ts, texture)
    def has_tag(self, name): return self.node.has_tag(name)
    def get_tag(self, name): return self.node.get_tag(name)
    def get_python_tag(self, name): return self.node.get_python_tag(name)
    def remove_node(self): return self.node.remove_node()
    def flatten_strong(self): return self.node.flatten_strong()
    def clear_model_nodes(self): return self.node.clear_model_nodes()
    def show(self): return self.node.show()
    def set_depth_offset(self, val): return self.node.set_depth_offset(val)
    def loop(self, val): return self.node.loop(val)
    def cleanup(self): return self.node.cleanup()
    def write_bam_file(self, fname): return self.node.write_bam_file(fname)

    def attach_node(self, name):
        return P3dNode(self.node.attach_new_node(name))

    def add_shape(self, shape):
        return self.node.node().add_shape(shape._mesh_shape)

    @property
    def name(self): return self.node.get_name()

    @property
    def node(self): return self.nodepath

    @property
    def p3dnode(self): return self.node.node()

    def set_pos(self, pos): return self.node.set_pos(pos._vec)

    def get_pos(self, other=None):
        return self.node.get_pos(* [] if other is None else [other.node])

    @property
    def x(self): return self.node.get_x()

    @property
    def y(self): return self.node.get_y()

    @property
    def z(self): return self.node.get_z()

    @property
    def hpr(self): return self.node.get_hpr()

    @property
    def h(self): return self.node.get_h()

    @property
    def p(self): return self.node.get_p()

    @property
    def r(self): return self.node.get_r()

    @property
    def scale(self): return self.node.get_scale()

    @property
    def is_empty(self): return self.node.is_empty()

    def get_relative_vector(self, node, vec):
        return self.node.get_relative_vector(node.node, vec)

    def set_material(self, mat): return self.node.set_material(mat, 1)

    def set_python_tag(self, name, val):
        return self.node.set_python_tag(name, val)

    def get_distance(self, other_node):
        return self.node.get_distance(other_node.node)

    def reparent_to(self, parent): return self.node.reparent_to(parent.node)

    def wrt_reparent_to(self, parent):
        return self.node.wrt_reparent_to(parent.node)

    @staticmethod
    def __get_pandanode(nodepath):
        if nodepath.has_python_tag('yyaglnode'):
            return nodepath.get_python_tag('yyaglnode')
        return P3dNode(nodepath)

    def find_all_matches(self, name):
        nodes = self.node.find_all_matches(name)
        return [self.__get_pandanode(node) for node in nodes]

    def find(self, name):
        model = self.node.find(name)
        if model: return self.__get_pandanode(model)

    def optimize(self):
        self.node.prepare_scene(base.win.get_gsg())
        self.node.premunge_scene(base.win.get_gsg())

    def hide(self, mask=None):
        return self.node.hide(*[] if mask is None else [mask])

    @property
    def tight_bounds(self): return self.node.get_tight_bounds()

    @property
    def parent(self): return self.node.get_parent()

    @property
    def children(self): return self.node.get_children()


class P3dAnimNode:

    def __init__(self, filepath, anim_dct):
        self.node = Actor(filepath, anim_dct)

    def loop(self, val): return self.node.loop(val)
    def reparent_to(self, node): self.node.reparent_to(node)

    @property
    def name(self): return self.node.get_name()

    def optimize(self):
        self.node.prepare_scene(base.win.get_gsg())
        self.node.premunge_scene(base.win.get_gsg())

    def set_omni(self):
        self.node.node().set_bounds(OmniBoundingVolume())
        self.node.node().set_final(True)

    def destroy(self): self.node.cleanup()


class P3dAmbientLight(object):

    def __init__(self, color):
        ambient_lgt = P3DAmbientLight('ambient light')
        ambient_lgt.set_color(color)
        self.ambient_np = render.attach_new_node(ambient_lgt)
        render.set_light(self.ambient_np)

    def destroy(self):
        render.clear_light(self.ambient_np)
        self.ambient_np.remove_node()


class P3dSpotlight(Facade):

    def __init__(self, mask=None):
        self.spot_lgt = render.attach_new_node(P3DSpotlight('spot'))
        snode = self.spot_lgt.node()
        snode.set_scene(render)
        snode.set_shadow_caster(True, 1024, 1024)
        snode.get_lens().set_fov(40)
        snode.get_lens().set_near_far(20, 200)
        if mask: snode.set_camera_mask(mask)
        render.set_light(self.spot_lgt)

    def set_pos(self, pos): return self.spot_lgt.set_pos(*pos)

    def look_at(self, pos): return self.spot_lgt.look_at(*pos)

    def set_color(self, color): return self.spot_lgt.set_color(*color)

    def destroy(self):
        render.clear_light(self.spot_lgt)
        self.spot_lgt.remove_node()
