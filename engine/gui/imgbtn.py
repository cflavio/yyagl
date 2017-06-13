from panda3d.core import Shader
from direct.gui.DirectButton import DirectButton
from direct.gui.DirectGuiGlobals import FLAT, ENTER, EXIT


class ImgBtn(DirectButton):

    def __init__(self, *args, **kwargs):
        DirectButton.__init__(self, *args, **kwargs)
        self['frameSize'] = (-1, 1, -1, 1)
        self['relief'] = FLAT
        shader_path = 'yyagl/assets/shaders/'
        shader = Shader.load(Shader.SL_GLSL, shader_path + 'filter.vert',
                             shader_path + 'imgbtn.frag')
        self.set_shader(shader)
        self.set_shader_input('col_offset', 0)
        self.set_shader_input('enable', 1)
        self.set_transparency(True)
        self.bind(ENTER, self._on_enter)
        self.bind(EXIT, self._on_exit)
        self.initialiseoptions(self.__class__)

    def _on_enter(self, pos):
        self.set_shader_input('col_offset', .25)

    def _on_exit(self, pos):
        self.set_shader_input('col_offset', 0)
