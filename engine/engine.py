from sys import path
from os.path import dirname, realpath
path.append(dirname(realpath(__file__)) + '/../thirdparty')
import __builtin__
from direct.showbase.ShowBase import ShowBase
from .pause import PauseMgr
from .profiler import Profiler
from .shader import ShaderMgr
from .gfx import EngineGfx
from .gui.gui import EngineGui
from .logic import EngineLogic
from .event import EngineEvent
from .audio import EngineAudio
from ..gameobject import GameObject
from .enginefacade import EngineFacade


class EngineShowBase(ShowBase):

    pass


class Engine(GameObject, EngineFacade):

    def __init__(self, cfg=None, on_end_cb=None):
        __builtin__.eng = self
        self.base = EngineShowBase()
        ShaderMgr(cfg.shaders_dev, cfg.gamma)
        Profiler(cfg.python_profiling, cfg.python_profiling_percall)
        comps = [
            [('logic', EngineLogic, [self, cfg])],
            [('gfx', EngineGfx, [self, cfg.model_path, cfg.antialiasing])],
            [('event', EngineEvent.init_cls(),
              [self, cfg.menu_joypad, on_end_cb])],
            [('gui', EngineGui.init_cls(), [self])],
            [('audio', EngineAudio, [self, cfg.volume])],
            [('pause', PauseMgr, [self])]]
        GameObject.__init__(self, comps)

    def destroy(self):
        GameObject.destroy(self)
        self.base.destroy()
