from direct.gui.DirectButton import DirectButton
from panda3d.core import Shader
from direct.gui.DirectGuiGlobals import FLAT, ENTER, EXIT


class ImageButton(DirectButton):

    def __init__(self, *args, **kwargs):
        DirectButton.__init__(self, *args, **kwargs)
        self['frameSize'] = (-1, 1, -1, 1)
        self['relief'] = FLAT
        shader = Shader.load(Shader.SL_GLSL,
                             'yyagl/assets/shaders/filter.vert',
                             'yyagl/assets/shaders/imgbtn.frag')
        self.setShader(shader)
        self.setShaderInput('col_scale', 0)
        self.setShaderInput('enable', 1)
        self.setTransparency(True)
        self.bind(ENTER, self._on_enter)
        self.bind(EXIT, self._on_exit)
        self.initialiseoptions(self.__class__)

    def _on_enter(self, pos):
        self.setShaderInput('col_scale', .25)

    def _on_exit(self, pos):
        self.setShaderInput('col_scale', 0)
