from sys import path
from os.path import dirname, realpath
path.append(dirname(realpath(__file__)) + '/../thirdparty')
from direct.showbase.ShowBase import ShowBase
from ..library.builder import LibraryBuilder
from .pause import PauseMgr
from .profiler import AbsProfiler
from .shader import ShaderMgr
from .log import LogMgr
from .font import FontMgr
from .phys import PhysMgr
from .gfx import EngineGfx
from .network.server import Server
from .network.client import Client
from .gui.gui import EngineGui
from .logic import EngineLogic
from .event import EngineEvent
from .audio import EngineAudio
from .lang import LangMgr
from ..gameobject import GameObject, Colleague
from .enginefacade import EngineFacade
from .configuration import Cfg


class EngineShowBase(ShowBase):

    pass


class Engine(GameObject, EngineFacade):

    def __init__(self, cfg=None):
        self.lib = LibraryBuilder.build()
        Colleague.eng = GameObject.eng = self
        EngineFacade.__init__(self)
        self.base = EngineShowBase()
        if not cfg: cfg = Cfg()
        self.shader_mgr = ShaderMgr(cfg.shaders_dev, cfg.gamma)
        self.profiler = AbsProfiler.build(cfg.py_profiling_percall)
        self.font_mgr = FontMgr()
        self.server = Server()
        self.client = Client()
        comps = [
            [('logic', EngineLogic, [self, cfg])],
            [('log_mgr', LogMgr.init_cls(), [self])],
            [('gfx', EngineGfx, [self, cfg.model_path, cfg.antialiasing])],
            [('phys_mgr', PhysMgr, [self])],
            [('event', EngineEvent.init_cls(),
              [self, cfg.menu_joypad])],
            [('gui', EngineGui.init_cls(), [self])],
            [('audio', EngineAudio, [self, cfg.volume])],
            [('pause', PauseMgr, [self])],
            [('lang_mgr', LangMgr, (cfg.lang, cfg.lang_domain,
                                    cfg.lang_path))]]

        GameObject.__init__(self, comps)

    def destroy(self):
        GameObject.destroy(self)
        self.base.destroy()
