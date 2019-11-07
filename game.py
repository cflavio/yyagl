from abc import ABCMeta
from .gameobject import LogicColleague, GameObject
from .engine.engine import Engine
from .facade import Facade


class GameLogic(LogicColleague):

    def on_start(self): pass


class GameFacade(Facade):

    def __init__(self):
        mth_lst = [('demand', lambda obj: obj.fsm.demand)]
        Facade.__init__(self, mth_lst=mth_lst)


class GameBase(GameObject, GameFacade):  # it doesn't manage the window
    __metaclass__ = ABCMeta

    def __init__(self, cfg, client_cls=None):
        GameFacade.__init__(self)
        self.logic = LogicColleague(self)
        self.eng = Engine(cfg, self.destroy, client_cls)
        GameObject.__init__(self)

    def destroy(self):
        self.logic.destroy()
        GameFacade.destroy(self)
        GameObject.destroy(self)
        # self.eng = self.eng.destroy()
        self.eng.server.destroy()
        self.eng.client.destroy()


class Game(GameBase):  # it adds the window

    def run(self):
        self.logic.on_start()
        base.run()
