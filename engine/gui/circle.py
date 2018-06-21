from yyagl.library.gui import Frame
from yyagl.library.panda.shader import load_shader


class Circle(Frame):

    def __init__(self, size=.4, pos=(.5, .5), parent=None, ray=.4, width=.05,
                 color_start=(1, 1, 0, 1), color_end=(0, 1, 0, 1)):
        Frame.__init__(self, pos=(pos[0], 1, pos[1]), textureCoord=True,
                       frameSize=(-size, size, -size, size), parent=parent)
        shader_dirpath = 'yyagl/assets/shaders/'
        shader = load_shader(shader_dirpath + 'filter.vert',
                             shader_dirpath + 'circle.frag')
        if shader:
            self.set_shader(shader)
            self.set_shader_input('ray', ray)
            self.set_shader_input('width', width)
            self.set_shader_input('color_start', color_start)
            self.set_shader_input('color_end', color_end)
            self.set_shader_input('progress', 1)
        self.set_transparency(True)

    @property
    def progress(self):
        return self.get_shader_input('progress')

    @progress.setter
    def progress(self, val):
        self.set_shader_input('progress', val)
