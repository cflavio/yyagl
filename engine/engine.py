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
from .gui.gui import EngineGui, EngineGuiWindow
from .phys import EnginePhys
from .logic import EngineLogic
from .event import EngineEvent, EngineEventWindow
from .audio import EngineAudio
from .network.server import Server
from .network.client import Client
from ..gameobject import GameObjectMdt


class EngineBase(ShowBase):

    pass


class Engine(GameObjectMdt):
    gui_cls = EngineGui
    event_cls = EngineEvent

    def __init__(self, cfg=None):
        __builtin__.eng = self
        self.base = EngineBase()
        init_lst = [
            [('logic', EngineLogic, [self, cfg])],
            [('log_mgr', LogMgr, [self])],
            [('lang_mgr', LangMgr, [self])],
            [('gfx', EngineGfx, [self])],
            [('phys', EnginePhys, [self])],
            [('gui', self.gui_cls, [self])],
            [('audio', EngineAudio, [self])],
            [('event', self.event_cls, [self])],
            [('pause', PauseMgr, [self])],
            [('font_mgr', FontMgr, [self])],
            [('server', Server, [self])],
            [('client', Client, [self])],
            [('shader_mgr', ShaderMgr, [self])]]
        GameObjectMdt.__init__(self, init_lst)

    def destroy(self):
        GameObjectMdt.destroy(self)
        self.base.destroy()


class EngineWindow(Engine):

    gui_cls = EngineGuiWindow
    event_cls = EngineEventWindow
