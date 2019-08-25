from yyagl.lib.gui import Btn
from yyagl.lib.p3d.shader import load_shader


class ImgBtn(Btn):

    def __init__(self, *args, **kwargs):
        Btn.__init__(self, *args, **kwargs)
        shader_dirpath = 'yyagl/assets/shaders/'
        shader = load_shader(shader_dirpath + 'filter.vert',
                             shader_dirpath + 'imgbtn.frag')
        if shader:
            self.set_shader(shader)
            shader_args = [('col_offset', 0), ('enable', 1)]
            list(map(lambda args: self.set_shader_input(*args), shader_args))
        self.set_transparency(True)

    def _on_enter(self, pos):  # pos comes from mouse
        self.set_shader_input('col_offset', .25)

    def _on_exit(self, pos):  # pos comes from mouse
        self.set_shader_input('col_offset', 0)

    def enable(self):
        super().enable()
        self.set_shader_input('enable', 1)

    def disable(self):
        super().disable()
        self.set_shader_input('enable', .2)
