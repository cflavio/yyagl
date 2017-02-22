from abc import ABCMeta
from .gameobject import Logic, GameObjectMdt
from .engine.engine import Engine, EngineWindow
import __builtin__


class GameLogic(Logic):

    def on_start(self):
        pass

    def on_end(self):
        pass


class Game(GameObjectMdt):
    __metaclass__ = ABCMeta
    engine_cls = Engine

    def __init__(self, init_lst, cfg):
        __builtin__.game = self
        eng = self.engine_cls(cfg)
        GameObjectMdt.__init__(self, init_lst)
        eng.event.register_close_cb(self.logic.on_end)
        self.logic.on_start()


class GameWindow(Game):
    #TODO do NoWindow in place of Window
    engine_cls = EngineWindow

    def __init__(self, init_lst, cfg):
        Game.__init__(self, init_lst, cfg)
        eng.base.run()
