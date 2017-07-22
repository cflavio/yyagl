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
        r_p = race_props
        init_lst = [
            [('fsm', RaceFsm, [self, race_props.shaders_dev])],
            [('gui', RaceGui, [self, r_p])],
            [('logic', self.logic_cls, [self, r_p])],
            [('event', self.event_cls, [self, r_p.ingame_menu, r_p.keys])]]
        GameObject.__init__(self, init_lst)
        RaceFacade.__init__(self)


class RaceSinglePlayer(Race):
    logic_cls = RaceLogicSinglePlayer


class RaceServer(Race):
    logic_cls = RaceLogicServer
    event_cls = RaceEventServer


class RaceClient(Race):
    logic_cls = RaceLogicClient
    event_cls = RaceEventClient
