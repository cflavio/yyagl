from yyagl.lib.p3d.gfx import RenderToTexture
from panda3d.core import TextureStage


class Signs(object):  # signs where we write supporters' names

    def __init__(self, nodes, draw_cb):
        self.nodes = nodes
        self.draw_cb = draw_cb
        self.rtts = []

    def set_signs(self): list(map(self.__set_sign, self.nodes))

    def __set_sign(self, node):
        self.rtts += [RenderToTexture()]
        self.draw_cb(self.rtts[-1].root)
        t_s = TextureStage('ts')
        t_s.setMode(TextureStage.MDecal)
        node.set_texture(t_s, self.rtts[-1].texture)

    def destroy(self):
        list(map(lambda rtt: rtt.destroy(), self.rtts))
        self.rtts = None
