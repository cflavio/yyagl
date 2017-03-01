from abc import ABCMeta
from .gameobject import Logic, GameObjectMdt
from .engine.engine import Engine
import __builtin__


class GameLogic(Logic):

    def on_start(self):
        pass

    def on_end(self):
        pass


class Game(GameObjectMdt):
    __metaclass__ = ABCMeta

    def __init__(self, init_lst, cfg):
        __builtin__.game = self
        eng = Engine(cfg)
        GameObjectMdt.__init__(self, init_lst)
        eng.event.register_close_cb(self.logic.on_end)
        self.logic.on_start()


class GameWindow(Game):
    #TODO do GameBase and Game in place of Window

    def __init__(self, init_lst, cfg):
        Game.__init__(self, init_lst, cfg)
        eng.base.run()
