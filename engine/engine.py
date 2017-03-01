from sys import path
from os.path import dirname, realpath
path.append(dirname(realpath(__file__)) + '/../thirdparty')
import __builtin__
from direct.showbase.ShowBase import ShowBase
from .pause import PauseMgr
from .font import FontMgr
from .log import LogMgr
from .lang import LangMgr
from .shader import ShaderMgr
from .gfx import EngineGfx
from .gui.gui import EngineGui
from .phys import EnginePhys
from .logic import EngineLogic
from .event import EngineEvent
from .audio import EngineAudio
from .network.server import Server
from .network.client import Client
from ..gameobject import GameObjectMdt


class EngineShowBase(ShowBase):

    pass


class Engine(GameObjectMdt):

    def __init__(self, cfg=None):
        __builtin__.eng = self
        self.base = EngineShowBase()
        init_lst = [
            [('logic', EngineLogic, [self, cfg])],
            [('log_mgr', LogMgr.init_cls(), [self])],
            [('lang_mgr', LangMgr, [self])],
            [('gfx', EngineGfx, [self, cfg.model_path, cfg.antialiasing])],
            [('phys', EnginePhys, [self])],
            [('gui', EngineGui.init_cls(), [self])],
            [('audio', EngineAudio, [self])],
            [('event', EngineEvent.init_cls(), [self, cfg.menu_joypad])],
            [('pause', PauseMgr, [self])],
            [('font_mgr', FontMgr, [self])],
            [('server', Server, [self])],
            [('client', Client, [self])],
            [('shader_mgr', ShaderMgr, [self])]]
        GameObjectMdt.__init__(self, init_lst)

    def destroy(self):
        GameObjectMdt.destroy(self)
        self.base.destroy()
