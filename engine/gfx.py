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
    def set_toon(): self.gfx_mgr.set_toon()

    def print_stats(self): self.gfx_mgr.print_stats()

    @staticmethod
    def particle(parent, pos, hpr, color, tot_time):
        Particle(parent, pos, hpr, color, tot_time)
