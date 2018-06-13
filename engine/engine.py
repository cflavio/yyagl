from sys import path
from os.path import dirname, realpath
path.append(dirname(realpath(__file__)) + '/../thirdparty')

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
from .network.xmpp import XMPP
from .gui.gui import EngineGui
from .logic import EngineLogic
from .event import EngineEvent
from .audio import EngineAudio
from .lang import LangMgr
from ..gameobject import GameObject, Colleague
from .enginefacade import EngineFacade
from .configuration import Cfg


class Engine(GameObject, EngineFacade):

    network_priority = -39

    def __init__(self, cfg=None, end_cb=None):
        self.upnp = False
        self.lib = LibraryBuilder.build()
        self.lib.configure()
        self.lib.init(end_cb=end_cb)
        Colleague.eng = GameObject.eng = self
        EngineFacade.__init__(self)
        cfg = cfg or Cfg()  # use a default conf if not provided
        self.shader_mgr = ShaderMgr(cfg.dev_cfg.shaders_dev, cfg.dev_cfg.gamma)
        self.profiler = AbsProfiler.build(cfg.profiling_cfg.pyprof_percall)
        self.font_mgr = FontMgr()
        self.server = Server()
        self.client = Client()
        self.xmpp = XMPP(cfg.dev_cfg.xmpp_server)
        comps = [
            [('logic', EngineLogic, [self, cfg])],
            [('log_mgr', LogMgr.init_cls(), [self])],
            [('gfx', EngineGfx, [self, cfg.dev_cfg.model_path, cfg.gui_cfg.antialiasing, cfg.gui_cfg.shaders])],
            [('phys_mgr', PhysMgr, [self])],
            [('event', EngineEvent, [self, cfg.dev_cfg.menu_joypad])],
            [('gui', EngineGui.init_cls(), [self])],
            [('audio', EngineAudio, [self, cfg.gui_cfg.volume])],
            [('pause', PauseMgr, [self])],
            [('lang_mgr', LangMgr, (cfg.lang_cfg.lang, cfg.lang_cfg.lang_domain,
                                    cfg.lang_cfg.lang_path))]]
        GameObject.__init__(self, comps)

    def destroy(self):
        GameObject.destroy(self)
        EngineFacade.destroy(self)
        self.lib.destroy()
        self.shader_mgr.destroy()
        self.profiler.destroy()
        self.font_mgr.destroy()
        self.server.destroy()
        self.client.destroy()
        self.xmpp.destroy()
        self.lib = self.shader_mgr = self.profiler = self.font_mgr = \
            self.server = self.client = None
        base.destroy()
