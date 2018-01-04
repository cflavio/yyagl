from panda3d.core import Shader
from direct.gui.DirectButton import DirectButton
from direct.gui.DirectGuiGlobals import FLAT, ENTER, EXIT, DISABLED, NORMAL
from yyagl.library.panda.shader import load_shader


class ImgBtn(DirectButton):

    def __init__(self, *args, **kwargs):
        DirectButton.__init__(self, *args, **kwargs)
        self['frameSize'] = (-1, 1, -1, 1)
        self['relief'] = FLAT
        shader_path = 'yyagl/assets/shaders/'
        shader = load_shader(shader_path + 'filter.vert',
                             shader_path + 'imgbtn.frag')
        if shader:
            self.set_shader(shader)
            self.set_shader_input('col_offset', 0)
            self.set_shader_input('enable', 1)
        self.set_transparency(True)
        self.bind(ENTER, self._on_enter)
        self.bind(EXIT, self._on_exit)
        self.initialiseoptions(self.__class__)

    def _on_enter(self, pos):
        # pos comes from mouse
        self.set_shader_input('col_offset', .25)

    def _on_exit(self, pos):
        # pos comes from mouse
        self.set_shader_input('col_offset', 0)

    def enable(self):
        self['state'] = NORMAL
        self.setShaderInput('enable', 1)

    def disable(self):
        self['state'] = DISABLED
        self.setShaderInput('enable', .2)
