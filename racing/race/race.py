from abc import ABCMeta
from yyagl.gameobject import GameObject
from yyagl.facade import Facade
from .logic import RaceLogic, RaceLogicSinglePlayer, RaceLogicServer, \
    RaceLogicClient
from .event import RaceEvent, RaceEventServer, RaceEventClient
from .gui.gui import RaceGui
from .fsm import RaceFsm, RaceFsmServer, RaceFsmClient


class RaceFacade(Facade):

    def __init__(self):
        self._fwd_mth('attach_obs', lambda obj: obj.event.attach)
        self._fwd_mth('detach_obs', lambda obj: obj.event.detach)
        self._fwd_prop('results', lambda obj: obj.gui.results)


class Race(GameObject, RaceFacade):
    __metaclass__ = ABCMeta
    logic_cls = RaceLogic
    event_cls = RaceEvent
    fsm_cls = RaceFsm

    def __init__(self, race_props):
        rpr = race_props
        init_lst = [
            [('fsm', self.fsm_cls, [self, rpr.shaders_dev])],
            [('gui', RaceGui, [self, rpr])],
            [('logic', self.logic_cls, [self, rpr])],
            [('event', self.event_cls, [self, rpr.ingame_menu, rpr.keys])]]
        GameObject.__init__(self, init_lst)
        RaceFacade.__init__(self)

    def destroy(self):
        GameObject.destroy(self)
        RaceFacade.destroy(self)


class RaceSinglePlayer(Race):
    logic_cls = RaceLogicSinglePlayer


class RaceServer(Race):
    logic_cls = RaceLogicServer
    event_cls = RaceEventServer
    fsm_cls = RaceFsmServer


class RaceClient(Race):
    logic_cls = RaceLogicClient
    event_cls = RaceEventClient
    fsm_cls = RaceFsmClient
