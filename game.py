import __builtin__
from abc import ABCMeta
from .gameobject import Logic, GameObject
from .engine.engine import Engine
from .facade import Facade


class GameLogic(Logic):

    def on_start(self): pass

    def on_end(self): pass


class GameFacade(Facade):

    def __init__(self): self._fwd_mth('demand', self.fsm.demand)


class GameBase(GameObject, GameFacade):  # it doesn't manage the window
    __metaclass__ = ABCMeta

    def __init__(self, init_lst, cfg):
        self.eng = Engine(cfg, self.on_end)
        GameObject.__init__(self, init_lst)
        GameFacade.__init__(self)
        self.eng.do_later(.001, self.logic.on_start)

    def on_end(self):
        # self.logic doesn't exist at __init__'s time
        self.logic.on_end()


class Game(GameBase):  # it adds the window

    def __init__(self, init_lst, cfg):
        GameBase.__init__(self, init_lst, cfg)

    def run(self):
        self.eng.base.run()
