from os import name
from yyagl.lib.gui import Frame
from yyagl.lib.p3d.shader import load_shader
from yyagl.gameobject import GameObject


class Circle(Frame, GameObject):

    def __init__(self, size=.4, pos=(0, 0), parent=None, ray=.4, thickness=.05,
                 col_start=(1, 1, 1, 1), col_end=(1, 1, 1, 1)):
        GameObject.__init__(self)
        Frame.__init__(self, pos=(pos[0], pos[1]), texture_coord=True,
                       frame_size=(-size, size, -size, size), parent=parent)
        path = 'yyagl/assets/shaders/'
        shader = load_shader(path + 'filter.vert', path + 'circle.frag')
        drv_lst = [self.eng.lib.driver_vendor, self.eng.lib.driver_renderer,
                   self.eng.lib.driver_version]
        is_nvidia = any('nvidia' in drv.lower() for drv in drv_lst)
        if shader and not (name == 'nt' and is_nvidia):
            self.set_shader(shader)
            args = [('ray', ray), ('width', thickness), ('progress', 0),
                    ('color_start', col_start), ('color_end', col_end)]
            map(lambda arg: self.set_shader_input(*arg), args)
        else: self['frameColor'] = (1, 1, 1, 0)
        self.set_transparency(True)

    @property
    def progress(self): return self.get_shader_input('progress')

    @progress.setter
    def progress(self, val): self.set_shader_input('progress', val)

    def destroy(self):
        Frame.destroy(self)
        GameObject.destroy(self)
