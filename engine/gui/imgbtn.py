from direct.gui.DirectButton import DirectButton
from panda3d.core import PNMImage, Texture, Filename, Shader
from itertools import product
from os.path import dirname, realpath
from direct.gui.DirectGuiGlobals import FLAT, ENTER, EXIT


vert = '''#version 130
in vec4 p3d_Vertex;
in vec2 p3d_MultiTexCoord0;
uniform mat4 p3d_ModelViewProjectionMatrix;
out vec2 texcoord;

void main() {
    gl_Position = p3d_ModelViewProjectionMatrix * p3d_Vertex;
    texcoord = p3d_MultiTexCoord0;
}'''


frag = '''#version 130
in vec2 texcoord;
uniform sampler2D p3d_Texture0;
uniform float col_scale;
out vec4 p3d_FragColor;

void main() {
    float dist_l = texcoord.x;
    float dist_r = 1 - texcoord.x;
    float dist_u = texcoord.y;
    float dist_b = 1 - texcoord.y;
    float alpha = min(dist_l, min(dist_r, min(dist_u, dist_b))) * 30;
    p3d_FragColor = (texture(p3d_Texture0, texcoord)  + vec4(col_scale, col_scale, col_scale, 1) ) * vec4(1, 1, 1, alpha);
}'''


class ImageButton(DirectButton):

    def __init__(self, *args, **kwargs):
        DirectButton.__init__(self, *args, **kwargs)
        self['frameSize'] = (-1, 1, -1, 1)
        self['relief'] = FLAT
        shader = Shader.make(Shader.SL_GLSL, vertex=vert, fragment=frag)
        self.setShader(shader)
        self.setShaderInput('col_scale', 0)
        self.setTransparency(True)
        self.bind(ENTER, self._on_enter)
        self.bind(EXIT, self._on_exit)
        self.initialiseoptions(self.__class__)

    def _on_enter(self, pos):
        self.setShaderInput('col_scale', .25)

    def _on_exit(self, pos):
        self.setShaderInput('col_scale', 0)
