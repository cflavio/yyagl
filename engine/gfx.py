from ..gameobject import GfxColleague
from .particle import Particle
from yyagl.lib.p3d.gfx import P3dGfxMgr, P3dAnimNode, P3dAmbientLight, \
    P3dSpotlight


GfxMgr = P3dGfxMgr
AnimNode = P3dAnimNode
AmbientLight = P3dAmbientLight
Spotlight = P3dSpotlight


class EngineGfx(GfxColleague):

    def __init__(self, mediator, model_path, antialiasing, shaders):
        GfxColleague.__init__(self, mediator)
        self.gfx_mgr = GfxMgr(model_path, antialiasing, shaders)
        self.root = None
        self.part2eff = {}
        if self.mediator.cfg.gui_cfg.shaders and \
                self.eng.lib.version.startswith('1.10'):
            # self.set_toon()
            self.set_bloom()

    def init(self):
        self.root = self.gfx_mgr.root.attach_node('world')

    def clean(self): self.root.remove_node()

    def load_model(self, filename, callback=None, extra_args=[], anim=None):
        return self.gfx_mgr.load_model(filename, callback, extra_args, anim)

    def set_toon(self): self.gfx_mgr.set_toon()

    def set_bloom(self): self.gfx_mgr.set_bloom()

    def print_stats(self): self.gfx_mgr.print_stats()

    @staticmethod
    def particle(parent, pos, hpr, color, tot_time):
        Particle(parent, pos, hpr, color, tot_time)
