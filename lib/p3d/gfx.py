from os.path import exists
from panda3d.core import get_model_path, AntialiasAttrib, PandaNode, \
    LightRampAttrib, Camera, OrthographicLens, NodePath, OmniBoundingVolume, \
    AmbientLight as P3DAmbientLight, Spotlight as P3DSpotlight, BitMask32, \
    Point2, Point3
from direct.filter.CommonFilters import CommonFilters
from direct.actor.Actor import Actor
from yyagl.racing.bitmasks import BitMasks


class RenderToTexture(object):

    def __init__(self):
        self.buffer = base.win.make_texture_buffer('result buffer', 256, 256)
        self.buffer.set_sort(-100)

        self.display_region = self.buffer.makeDisplayRegion()
        self.display_region.set_sort(20)

        self.camera = NodePath(Camera('camera 2d'))
        lens = OrthographicLens()
        lens.set_film_size(1, 1)
        lens.set_near_far(-1000, 1000)
        self.camera.node().set_lens(lens)

        self.root = NodePath('result render')
        self.root.set_depth_test(False)
        self.root.set_depth_write(False)
        self.camera.reparent_to(self.root)
        self.display_region.set_camera(self.camera)

    @property
    def texture(self): return self.buffer.get_texture()

    def destroy(self):
        base.graphicsEngine.remove_window(self.buffer)
        if base.win:  # if you close the window during a race
            base.win.remove_display_region(self.display_region)
        map(lambda node: node.remove_node(), [self.camera, self.root])


class P3dGfxMgr(object):

    def __init__(self):
        self.root = P3dNode(render)
        self.callbacks = {}
        self.filters = None

    def init(self, model_path, antialiasing, shaders):
        get_model_path().append_directory(model_path)
        if base.appRunner:
            root_dir = base.appRunner.p3dFilename.get_dirname()
            get_model_path().append_directory(root_dir + '/' + model_path)
            get_model_path().append_directory(root_dir)
        render.set_shader_auto()
        render.set_two_sided(True)
        if antialiasing:
            render.set_antialias(AntialiasAttrib.MAuto)
        if shaders and base.win:
            self.filters = CommonFilters(base.win, base.cam)

    def _intermediate_cb(self, model, fpath):
        return self.callbacks[fpath](P3dNode(model))

    def load_model(self, filename, callback=None, extra_args=[], anim=None):
        ext = '.bam' if exists(filename + '.bam') else ''
        if anim:
            anim_dct = {'anim': filename + '-Anim' + ext}
            return P3dNode(Actor(filename + ext, anim_dct))
        elif callback:
            self.callbacks[filename + ext] = callback
            return loader.loadModel(
              filename + ext, callback=self._intermediate_cb,
              extraArgs=extra_args + [filename + ext])
        else:
            return P3dNode(loader.loadModel(filename + ext))

    def set_toon(self):
        tempnode = NodePath(PandaNode('temp node'))
        tempnode.set_attrib(LightRampAttrib.make_single_threshold(.5, .4))
        tempnode.set_shader_auto()
        base.cam.node().set_initial_state(tempnode.get_state())
        self.filters.set_cartoon_ink(separation=1)

    def set_bloom(self):
        if not base.win: return
        self.filters.setBloom(
            blend=(.3, .4, .3, 0),  # default: (.3, .4, .3, 0)
            mintrigger=.6,  # default: .6
            maxtrigger=1.0,  # default: 1.0
            desat=.6,  # default: .6
            intensity=1.0,  # default: 1.0
            size='medium'  # default: 'medium' ('small', 'medium', 'large')
        )

    @staticmethod
    def pos2d(node):
        p3d = base.cam.get_relative_point(node.node, Point3(0, 0, 0))
        p2d = Point2()
        return p2d if base.camLens.project(p3d, p2d) else None

    @property
    def shader_support(self):
        return base.win.get_gsg().get_supports_basic_shaders()

    @staticmethod
    def set_shader(val):
        (render.set_shader_auto if val else render.set_shader_off)()

    @staticmethod
    def set_blur(): pass  # self.filters.setBlurSharpen(.5)

    @staticmethod
    def print_stats():
        print '\n\n#####\nrender2d.analyze()'
        base.render2d.analyze()
        print '\n\n#####\nrender.analyze()'
        base.render.analyze()
        print '\n\n#####\nrender2d.ls()'
        base.render2d.ls()
        print '\n\n#####\nrender.ls()'
        base.render.ls()


class P3dNode(object):

    def __init__(self, np):
        self.node = np
        self.node.set_python_tag('pandanode', self)

    def attach_node(self, name):
        return P3dNode(self.node.attach_new_node(name))

    def add_shape(self, shape):
        return self.node.node().add_shape(shape.mesh_shape)

    def get_name(self): return self.node.get_name()

    def get_node(self): return self.node.node()

    def set_collide_mask(self, mask): return self.node.set_collide_mask(mask)

    def set_pos(self, pos): return self.node.set_pos(pos.vec)

    def set_x(self, x): return self.node.set_x(x)

    def set_y(self, y): return self.node.set_y(y)

    def set_z(self, z): return self.node.set_z(z)

    def get_pos(self, other=None):
        return self.node.get_pos(* [] if other is None else [other.node])

    def get_x(self): return self.node.get_x()

    def get_y(self): return self.node.get_y()

    def get_z(self): return self.node.get_z()

    @property
    def x(self): return self.get_x()

    @property
    def y(self): return self.get_y()

    @property
    def z(self): return self.get_z()

    def set_hpr(self, hpr): return self.node.set_hpr(hpr)

    def set_h(self, h): return self.node.set_h(h)

    def set_p(self, p): return self.node.set_p(p)

    def set_r(self, r): return self.node.set_r(r)

    def get_hpr(self): return self.node.get_hpr()

    def get_h(self): return self.node.get_h()

    def get_p(self): return self.node.get_p()

    def get_r(self): return self.node.get_r()

    def set_scale(self, scale): return self.node.set_scale(scale)

    def get_scale(self): return self.node.get_scale()

    def get_transform(self, node): return self.node.get_transform(node.node)

    def get_relative_vector(self, node, vec):
        return self.node.get_relative_vector(node.node, vec)

    def set_transparency(self, val): return self.node.set_transparency(val)

    def set_alpha_scale(self, val): return self.node.set_alpha_scale(val)

    def set_material(self, material): return self.node.set_material(material, 1)

    def set_texture(self, ts, texture):
        return self.node.set_texture(ts, texture)

    def has_tag(self, name): return self.node.has_tag(name)

    def get_tag(self, name): return self.node.get_tag(name)

    def get_python_tag(self, name): return self.node.get_python_tag(name)

    def set_python_tag(self, name, val):
        return self.node.set_python_tag(name, val)

    def remove_node(self): return self.node.remove_node()

    def is_empty(self): return self.node.is_empty()

    def get_distance(self, other_node):
        return self.node.get_distance(other_node.node)

    def reparent_to(self, parent): return self.node.reparent_to(parent.node)

    def wrt_reparent_to(self, parent):
        return self.node.wrt_reparent_to(parent.node)

    @staticmethod
    def __get_pandanode(nodepath):
        if nodepath.has_python_tag('pandanode'):
            return nodepath.get_python_tag('pandanode')
        return P3dNode(nodepath)

    def find_all_matches(self, name):
        nodes = self.node.find_all_matches(name)
        return [self.__get_pandanode(node) for node in nodes]

    def find(self, name):
        model = self.node.find(name)
        if model: return self.__get_pandanode(model)

    def flatten_strong(self): return self.node.flatten_strong()

    def prepare_scene(self): return self.node.prepare_scene(base.win.get_gsg())

    def premunge_scene(self):
        return self.node.premunge_scene(base.win.get_gsg())

    def clear_model_nodes(self): return self.node.clear_model_nodes()

    def show(self): return self.node.show()

    def hide(self, mask=None):
        return self.node.hide(*[] if mask is None else [mask])

    def set_depth_offset(self, offset):
        return self.node.set_depth_offset(offset)

    def get_tight_bounds(self): return self.node.get_tight_bounds()

    def get_parent(self): return self.node.get_parent()

    def get_children(self): return self.node.get_children()

    def loop(self, name): return self.node.loop(name)

    def cleanup(self): return self.node.cleanup()

    def write_bam_file(self, fpath): self.node.write_bam_file(fpath)


class P3dAnimNode(object):

    def __init__(self, path, anim_dct):
        self.node = Actor(path, anim_dct)

    def loop(self, anim_name): return self.node.loop(anim_name)

    def reparent_to(self, parent): return self.node.reparent_to(parent)

    def get_name(self): return self.node.get_name()

    def set_omni(self):
        self.node.node().set_bounds(OmniBoundingVolume())
        self.node.node().set_final(True)

    def destroy(self):
        self.node.cleanup()


class P3dAmbientLight(object):

    def __init__(self, color):
        ambient_lgt = P3DAmbientLight('ambient light')
        ambient_lgt.set_color(color)
        self.ambient_np = render.attach_new_node(ambient_lgt)
        render.set_light(self.ambient_np)

    def destroy(self):
        render.clear_light(self.ambient_np)
        self.ambient_np.remove_node()


class P3dSpotlight(object):

    def __init__(self):
        self.spot_lgt = render.attach_new_node(P3DSpotlight('spot'))
        self.spot_lgt.node().set_scene(render)
        self.spot_lgt.node().set_shadow_caster(True, 1024, 1024)
        self.spot_lgt.node().get_lens().set_fov(40)
        self.spot_lgt.node().get_lens().set_near_far(20, 200)
        self.spot_lgt.node().set_camera_mask(BitMask32.bit(BitMasks.general))
        render.set_light(self.spot_lgt)

    def set_pos(self, pos): return self.spot_lgt.set_pos(*pos)

    def look_at(self, pos): return self.spot_lgt.look_at(*pos)

    def set_color(self, color): return self.spot_lgt.set_color(*color)

    def destroy(self):
        render.clear_light(self.spot_lgt)
        self.spot_lgt.remove_node()
