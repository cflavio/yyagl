from panda3d.core import get_model_path, LightRampAttrib, PandaNode, \
    NodePath, AntialiasAttrib
from direct.filter.CommonFilters import CommonFilters
from ..gameobject import Gfx
from .particle import Particle
from yyagl.library.panda.gfx import PandaGfxMgr


GfxMgr = PandaGfxMgr


class EngineGfx(Gfx):

    def __init__(self, mdt, model_path, antialiasing):
        Gfx.__init__(self, mdt)
        self.gfx_mgr = GfxMgr()
        self.gfx_mgr.init(model_path, antialiasing)
        self.root = None
        self.part2eff = {}

    def init(self):
        self.root = self.gfx_mgr.root.attach_node('world')

    def clean(self): self.root.remove_node()

    def load_model(self, filename, callback=None, extra_args=[], anim=None):
        return self.gfx_mgr.load_model(filename, callback, extra_args, anim)

    @staticmethod
    def set_toon():
        tempnode = NodePath(PandaNode('temp node'))
        tempnode.setAttrib(LightRampAttrib.make_single_threshold(.5, .4))
        tempnode.set_shader_auto()
        base.cam.node().set_initial_state(tempnode.get_state())
        CommonFilters(base.win, base.cam).setCartoonInk(separation=1)

    def print_stats(self):
        print '\n\n#####\nrender2d.analyze()'
        base.render2d.analyze()
        print '\n\n#####\nrender.analyze()'
        base.render.analyze()
        print '\n\n#####\nrender2d.ls()'
        base.render2d.ls()
        print '\n\n#####\nrender.ls()'
        base.render.ls()

    @staticmethod
    def particle(parent, pos, hpr, color, tot_time):
        Particle(parent, pos, hpr, color, tot_time)
