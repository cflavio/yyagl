from abc import ABCMeta
from yyagl.gameobject import GameObject
from yyagl.facade import Facade
from .logic import RaceLogic, RaceLogicSinglePlayer, RaceLogicServer, \
    RaceLogicClient
from .event import RaceEvent, RaceEventServer, RaceEventClient
from .gui.gui import RaceGui, RaceGuiServer
from .fsm import RaceFsm, RaceFsmServer, RaceFsmClient


class RaceFacade(Facade):

    def __init__(self):
        prop_lst = [('results', lambda obj: obj.gui.results)]
        mth_lst = [
            ('attach_obs', lambda obj: obj.event.attach),
            ('detach_obs', lambda obj: obj.event.detach)]
        Facade.__init__(self, prop_lst, mth_lst)


class Race(GameObject, RaceFacade):
    __metaclass__ = ABCMeta
    logic_cls = RaceLogic
    event_cls = RaceEvent
    fsm_cls = RaceFsm
    gui_cls = RaceGui

    def __init__(self, race_props, players):
        rpr = race_props
        GameObject.__init__(self)
        self.fsm = self.fsm_cls(self, rpr.shaders_dev)
        self.gui = self.gui_cls(self, rpr, players)
        self.logic = self.logic_cls(self, rpr)
        self.event = self.event_cls(self, rpr.ingame_menu, rpr.keys, players)
        RaceFacade.__init__(self)

    def destroy(self):
        self.fsm.destroy()
        self.gui.destroy()
        self.logic.destroy()
        self.event.destroy()
        GameObject.destroy(self)
        RaceFacade.destroy(self)


class RaceSinglePlayer(Race):
    logic_cls = RaceLogicSinglePlayer


class RaceServer(Race):
    logic_cls = RaceLogicClient
    event_cls = RaceEventServer
    fsm_cls = RaceFsmClient
    gui_cls = RaceGuiServer


class RaceClient(Race):
    logic_cls = RaceLogicClient
    event_cls = RaceEventClient
    fsm_cls = RaceFsmClient
