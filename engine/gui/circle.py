from os import name
from yyagl.library.gui import Frame
from yyagl.library.panda.shader import load_shader
from yyagl.gameobject import GameObject


class Circle(Frame, GameObject):

    def __init__(self, size=.4, pos=(.5, .5), parent=None, ray=.4, width=.05,
                 color_start=(1, 1, 0, 1), color_end=(0, 1, 0, 1)):
        GameObject.__init__(self)
        Frame.__init__(self, pos=(pos[0], 1, pos[1]), textureCoord=True,
                       frameSize=(-size, size, -size, size), parent=parent)
        shader_dirpath = 'yyagl/assets/shaders/'
        shader = load_shader(shader_dirpath + 'filter.vert',
                             shader_dirpath + 'circle.frag')
        drv_lst = [self.eng.lib.driver_vendor(), self.eng.lib.driver_renderer(),
                   self.eng.lib.driver_version()]
        is_nvidia = any('nvidia' in drv.lower() for drv in drv_lst)
        if shader and not (name == 'nt' and is_nvidia):
            self.set_shader(shader)
            self.set_shader_input('ray', ray)
            self.set_shader_input('width', width)
            self.set_shader_input('color_start', color_start)
            self.set_shader_input('color_end', color_end)
            self.set_shader_input('progress', 1)
        else: self['frameColor'] = (1, 1, 1, 0)
        self.set_transparency(True)

    @property
    def progress(self):
        return self.get_shader_input('progress')

    @progress.setter
    def progress(self, val):
        self.set_shader_input('progress', val)

    def destroy(self):
        Frame.destroy(self)
        GameObject.destroy(self)
