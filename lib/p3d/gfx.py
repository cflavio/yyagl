from os.path import exists
from panda3d.core import get_model_path, AntialiasAttrib, PandaNode, \
    LightRampAttrib, Camera, OrthographicLens, NodePath, OmniBoundingVolume, \
    AmbientLight as P3DAmbientLight, Spotlight as P3DSpotlight, BitMask32, \
    Point2, Point3
from direct.filter.CommonFilters import CommonFilters
from direct.actor.Actor import Actor
from yyagl.lib.p3d.p3d import LibP3d
from yyagl.facade import Facade


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
        map(lambda node: node.remove_node(), [self.camera, self.root])
        self.buffer = self.display_region = self.camera = self.root = None


class P3dGfxMgr(object):

    def __init__(self, model_path, antialiasing, shaders):
        self.root = P3dNode(render)
        self.callbacks = {}
        self.filters = None
        get_model_path().append_directory(model_path)
        if base.appRunner:
            root_dir = base.appRunner.p3dFilename.get_dirname()
            paths = [root_dir + '/' + model_path, root_dir]
            map(get_model_path().append_directory, paths)
        render.set_shader_auto()
        render.set_two_sided(True)
        if antialiasing: render.set_antialias(AntialiasAttrib.MAuto)
        if shaders and base.win:
            self.filters = CommonFilters(base.win, base.cam)

    def load_model(self, filename, callback=None, extra_args=[], anim=None):
        ext = '.bam' if exists(filename + '.bam') else ''
        if anim:
            anim_dct = {'anim': filename + '-Anim' + ext}
            return P3dNode(Actor(filename + ext, anim_dct))
        elif callback:
            return loader.loadModel(
              filename + ext, callback=lambda model: callback(P3dNode(model)))
        else:
            return P3dNode(loader.loadModel(LibP3d.p3dpath(filename + ext)))

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
            print '\n\n#####\n%s()' % elm[0]
            elm[1]()


class P3dNode(Facade):

    def __init__(self, nodepath):
        self.nodepath = nodepath
        self.node.set_python_tag('yyaglnode', self)
        mth_lst = [
            ('set_collide_mask', lambda obj: obj.node.set_collide_mask),
            ('set_x', lambda obj: obj.node.set_x),
            ('set_y', lambda obj: obj.node.set_y),
            ('set_z', lambda obj: obj.node.set_z),
            ('set_hpr', lambda obj: obj.node.set_hpr),
            ('set_h', lambda obj: obj.node.set_h),
            ('set_p', lambda obj: obj.node.set_p),
            ('set_r', lambda obj: obj.node.set_r),
            ('set_scale', lambda obj: obj.node.set_scale),
            ('set_transparency', lambda obj: obj.node.set_transparency),
            ('set_alpha_scale', lambda obj: obj.node.set_alpha_scale),
            ('set_texture', lambda obj: obj.node.set_texture),
            ('has_tag', lambda obj: obj.node.has_tag),
            ('get_tag', lambda obj: obj.node.get_tag),
            ('get_python_tag', lambda obj: obj.node.get_python_tag),
            ('remove_node', lambda obj: obj.node.remove_node),
            ('flatten_strong', lambda obj: obj.node.flatten_strong),
            ('clear_model_nodes', lambda obj: obj.node.clear_model_nodes),
            ('show', lambda obj: obj.node.show),
            ('set_depth_offset', lambda obj: obj.node.set_depth_offset),
            ('loop', lambda obj: obj.node.loop),
            ('cleanup', lambda obj: obj.node.cleanup),
            ('write_bam_file', lambda obj: obj.node.write_bam_file)]
        Facade.__init__(self, mth_lst=mth_lst)

    def attach_node(self, name):
        return P3dNode(self.node.attach_new_node(name))

    def add_shape(self, shape):
        return self.node.node().add_shape(shape.mesh_shape)

    @property
    def name(self): return self.node.get_name()

    @property
    def node(self): return self.nodepath

    @property
    def p3dnode(self): return self.node.node()

    def set_pos(self, pos): return self.node.set_pos(pos.vec)

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

    def set_material(self, material): return self.node.set_material(material, 1)

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


class P3dAnimNode(Facade):

    def __init__(self, filepath, anim_dct):
        self.node = Actor(filepath, anim_dct)
        mth_lst = [
            ('loop', lambda obj: obj.node.loop),
            ('reparent_to', lambda obj: obj.node.reparent_to)]
        Facade.__init__(self, mth_lst=mth_lst)

    @property
    def name(self): return self.node.get_name()

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
