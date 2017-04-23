from abc import ABCMeta
from .gameobject import Logic, GameObject
from .engine.engine import Engine
import __builtin__


class GameLogic(Logic):

    def on_start(self):
        pass

    def on_end(self):
        pass


class GameFacade(object):

    def demand(self, state):
        return self.fsm.demand(state)


class GameBase(GameObject, GameFacade):  # it doesn't manage the window
    __metaclass__ = ABCMeta

    def __init__(self, init_lst, cfg):
        __builtin__.game = self
        eng = Engine(cfg)
        GameObject.__init__(self, init_lst)
        eng.register_end_cb(self.logic.on_end)
        self.logic.on_start()


class Game(GameBase):  # it adds the window

    def __init__(self, init_lst, cfg):
        GameBase.__init__(self, init_lst, cfg)
        eng.base.run()
