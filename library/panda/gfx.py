from os.path import exists
from panda3d.core import get_model_path, AntialiasAttrib, NodePath, PandaNode as P3DNode, LightRampAttrib
from direct.filter.CommonFilters import CommonFilters
from direct.actor.Actor import Actor
from ..gfx import GfxMgr, Node


class PandaGfxMgr(GfxMgr):

    def __init__(self):
        self.root = PandaNode(render)
        self.callbacks = {}

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
        if shaders:
            self.filters = CommonFilters(base.win, base.cam)

    def _intermediate_cb(self, model, fpath):
        return self.callbacks[fpath](PandaNode(model))

    def load_model(self, filename, callback=None, extra_args=[], anim=None):
        ext = '.bam' if exists(filename + '.bam') else ''
        if anim:
            return PandaNode(Actor(filename + ext, {'anim': filename + '-Anim' + ext}))
        elif callback:
            self.callbacks[filename + ext] = callback
            return loader.loadModel(filename + ext, callback=self._intermediate_cb, extraArgs=extra_args + [filename + ext])
        else:
            return PandaNode(loader.loadModel(filename + ext))

    def set_toon(self):
        tempnode = NodePath(P3DNode('temp node'))
        tempnode.set_attrib(LightRampAttrib.make_single_threshold(.5, .4))
        tempnode.set_shader_auto()
        base.cam.node().set_initial_state(tempnode.get_state())
        self.filters.set_cartoon_ink(separation=1)

    def set_bloom(self):
        self.filters.setBloom(
            blend=(.3, .4, .3, 0),  # default: (.3, .4, .3, 0)
            mintrigger=.6,  # default: .6
            maxtrigger=1.0,  # default: 1.0
            desat=.6,  # default: .6
            intensity=1.0,  # default: 1.0
            size='medium'  # default: 'medium' ('small', 'medium', 'large')
        )

    def set_blur(self):
        pass # self.filters.setBlurSharpen(.5)

    def print_stats(self):
        print '\n\n#####\nrender2d.analyze()'
        base.render2d.analyze()
        print '\n\n#####\nrender.analyze()'
        base.render.analyze()
        print '\n\n#####\nrender2d.ls()'
        base.render2d.ls()
        print '\n\n#####\nrender.ls()'
        base.render.ls()


class PandaNode(Node):

    def __init__(self, np):
        Node.__init__(self)
        self.node = np
        self.node.set_python_tag('pandanode', self)

    def attach_node(self, name): return PandaNode(self.node.attach_new_node(name))

    def add_shape(self, shape):
        return self.node.node().add_shape(shape)

    def get_name(self): return self.node.get_name()

    def get_node(self): return self.node.node()

    def set_collide_mask(self, mask): return self.node.set_collide_mask(mask)

    def set_pos(self, pos): return self.node.set_pos(pos)

    def set_x(self, x): return self.node.set_x(x)

    def set_y(self, y): return self.node.set_y(y)

    def set_z(self, z): return self.node.set_z(z)

    def get_pos(self, other=None):
        return self.node.get_pos(* [] if other is None else [other.node])

    def get_x(self): return self.node.get_x()

    def get_y(self): return self.node.get_y()

    def get_z(self): return self.node.get_z()

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

    def get_relative_vector(self, node, vec): return self.node.get_relative_vector(node.node, vec)

    def set_transparency(self, val): return self.node.set_transparency(val)

    def set_alpha_scale(self, val): return self.node.set_alpha_scale(val)

    def set_material(self, material): return self.node.set_material(material, 1)

    def set_texture(self, ts, texture): return self.node.set_texture(ts, texture)

    def has_tag(self, name): return self.node.has_tag(name)

    def get_tag(self, name): return self.node.get_tag(name)

    def get_python_tag(self, name): return self.node.get_python_tag(name)

    def set_python_tag(self, name, val): return self.node.set_python_tag(name, val)

    def remove_node(self): return self.node.remove_node()

    def is_empty(self): return self.node.is_empty()

    def get_distance(self, other_node): return self.node.get_distance(other_node.node)

    def reparent_to(self, parent): return self.node.reparent_to(parent.node)

    def wrt_reparent_to(self, parent): return self.node.wrt_reparent_to(parent.node)

    def __get_pandanode(self, np):
        if np.has_python_tag('pandanode'): return np.get_python_tag('pandanode')
        return PandaNode(np)

    def find_all_matches(self, name):
        return [self.__get_pandanode(node) for node in self.node.find_all_matches(name)]

    def find(self, name):
        model = self.node.find(name)
        if model: return self.__get_pandanode(model)

    def flatten_strong(self): return self.node.flatten_strong()

    def prepare_scene(self): return self.node.prepare_scene(base.win.get_gsg())

    def premunge_scene(self): return self.node.premunge_scene(base.win.get_gsg())

    def clear_model_nodes(self): return self.node.clear_model_nodes()

    def show(self): return self.node.show()

    def hide(self, mask=None):
        return self.node.hide(*[] if mask is None else [mask])

    def set_depth_offset(self, offset): return self.node.set_depth_offset(offset)

    def get_tight_bounds(self): return self.node.get_tight_bounds()

    def get_parent(self): return self.node.get_parent()

    def get_children(self): return self.node.get_children()

    def loop(self, name): return self.node.loop(name)

    def cleanup(self): return self.node.cleanup()

    def write_bam_file(self, fpath): self.node.write_bam_file(fpath)
