class GfxMgr(object):

    @staticmethod
    def init(model_path, antialiasing): pass

    def load_model(self, filename, callback=None, extra_args=[], anim=None):
        pass


class Node(object):

    def __init__(self): pass

    def attach_node(self, name): pass

    def add_shape(self, shape): pass

    def get_name(self): pass

    def get_node(self): pass

    def set_collide_mask(self, mask): pass

    def set_pos(self, pos): pass

    def set_x(self, x): pass

    def set_y(self, y): pass

    def set_z(self, z): pass

    def get_pos(self, other=None): pass

    def get_x(self): pass

    def get_y(self): pass

    def get_z(self): pass

    def set_hpr(self, hpr): pass

    def set_h(self, heading): pass

    def set_p(self, pitch): pass

    def set_r(self, roll): pass

    def get_hpr(self): pass

    def get_h(self): pass

    def get_p(self): pass

    def get_r(self): pass

    def set_scale(self, scale): pass

    def get_scale(self): pass

    def get_transform(self, node): pass

    def get_relative_vector(self, node, vec): pass

    def set_transparency(self, val): pass

    def set_alpha_scale(self, val): pass

    def set_material(self, material): pass

    def set_texture(self, texture_stage, texture): pass

    def has_tag(self, name): pass

    def get_tag(self, name): pass

    def get_python_tag(self, name): pass

    def set_python_tag(self, name, val): pass

    def remove_node(self): pass

    def is_empty(self): pass

    def get_distance(self, other_node): pass

    def reparent_to(self, parent): pass

    def wrt_reparent_to(self, parent): pass

    def find_all_matches(self, name): pass

    def find(self, name): pass

    def flatten_strong(self): pass

    def prepare_scene(self): pass

    def premunge_scene(self): pass

    def clear_model_nodes(self): pass

    def show(self): pass

    def hide(self, mask=None): pass

    def set_depth_offset(self, offset): pass

    def get_tight_bounds(self): pass

    def get_parent(self): pass

    def get_children(self): pass

    def loop(self, name): pass

    def cleanup(self): pass

    def write_bam_file(self, fpath): pass


class AnimNode(object):

    def __init__(self): pass


class AmbientLight(object):

    def __init__(self): pass


class Spotlight(object):

    def __init__(self): pass
