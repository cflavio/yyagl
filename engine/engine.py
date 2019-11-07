from sys import path
from os.path import dirname, realpath
path.append(dirname(realpath(__file__)) + '/../thirdparty')

from ..lib.builder import LibBuilder
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
from .cbmux import CallbackMux
from .clock import Clock


class Engine(GameObject, EngineFacade):

    network_priority = -39

    def __init__(self, cfg=None, end_cb=None, client_cls=None):
        self.lib = LibBuilder.build()
        self.lib.configure()
        self.lib.init(end_cb=end_cb)
        Colleague.eng = GameObject.eng = self
        EngineFacade.__init__(self)
        cfg = cfg or Cfg()  # use a default conf if not provided
        self.shader_mgr = ShaderMgr(cfg.dev_cfg.shaders_dev, cfg.dev_cfg.gamma)
        self.profiler = AbsProfiler.build(cfg.profiling_cfg.pyprof_percall)
        self.font_mgr = FontMgr()
        self.server = Server(cfg.dev_cfg.port)
        self.client = (client_cls or Client)(cfg.dev_cfg.port, cfg.dev_cfg.server)
        self.cb_mux = CallbackMux()
        self.logic = EngineLogic(self, cfg)
        self.log_mgr = LogMgr.init_cls()(self)
        self.gfx = EngineGfx(self, cfg.dev_cfg.model_path,
                             cfg.gui_cfg.antialiasing,
                             cfg.gui_cfg.shaders,
                             cfg.gui_cfg.fixed_fps,
                             cfg.dev_cfg.srgb)
        self.phys_mgr = PhysMgr(self)
        self.event = EngineEvent(self, cfg.dev_cfg.menu_joypad)
        self.gui = EngineGui.init_cls()(self)
        self.audio = EngineAudio(self, cfg.gui_cfg.volume)
        self.pause = PauseMgr(self)
        self.lang_mgr = LangMgr(cfg.lang_cfg.lang,
                                cfg.lang_cfg.lang_domain,
                                cfg.lang_cfg.lang_path)
        GameObject.__init__(self)
        self.clock = Clock(self.pause)

    def destroy(self):
        GameObject.destroy(self)
        EngineFacade.destroy(self)
        self.lib.destroy()
        self.shader_mgr.destroy()
        self.profiler.destroy()
        self.font_mgr.destroy()
        self.server.destroy()
        self.client.destroy()
        #self.xmpp.destroy()
        self.logic.destroy()
        self.log_mgr.destroy()
        self.gfx.destroy()
        self.phys_mgr.destroy()
        self.event.destroy()
        self.gui.destroy()
        self.audio.destroy()
        self.pause.destroy()
        self.lang_mgr.destroy()
        self.lib = self.shader_mgr = self.profiler = self.font_mgr = \
            self.server = self.client = None
        base.destroy()
