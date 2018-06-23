class LibShaderMgr(object):

    def __init__(self, shaders, gamma): pass

    def set_amb_lgt(self, col): pass

    def set_dir_lgt(self, col, direction): pass

    def set_pnt_lgt(self, col, pos): pass

    def set_spotlight(self, col, exp, cutoff, pos, look_at): pass

    @staticmethod
    def set_default_args(idx): pass

    def set_lgt_args(self, idx, lgt): pass

    def clear_lights(self): pass

    def setup_post_fx(self): pass

    def apply(self): pass

    def toggle_shader(self): pass

    def set_shader_pars(self, model): pass

    def __set_slots(self, texture_stage, model, slot): pass

    def destroy(self): pass
