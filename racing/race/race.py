from abc import ABCMeta
from yyagl.gameobject import GameObject
from yyagl.facade import Facade
from .logic import RaceLogic, RaceLogicSinglePlayer, RaceLogicServer, \
    RaceLogicClient
from .event import RaceEvent, RaceEventServer, RaceEventClient
from .gui.gui import RaceGui
from .fsm import RaceFsm


class RaceFacade(Facade):

    def __init__(self):
        self._fwd_mth('attach_obs', self.event.attach)
        self._fwd_mth('detach_obs', self.event.detach)
        self._fwd_prop('results', self.gui.results)


class Race(GameObject, RaceFacade):
    __metaclass__ = ABCMeta
    logic_cls = RaceLogic
    event_cls = RaceEvent

    def __init__(self, race_props):
        rpr = race_props
        init_lst = [
            [('fsm', RaceFsm, [self, rpr.shaders_dev])],
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


class RaceClient(Race):
    logic_cls = RaceLogicClient
    event_cls = RaceEventClient
