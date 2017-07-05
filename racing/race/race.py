from abc import ABCMeta
from yyagl.gameobject import GameObject
from .logic import RaceLogic, RaceLogicSinglePlayer, RaceLogicServer, \
    RaceLogicClient
from .event import RaceEvent, RaceEventServer, RaceEventClient
from .gui.gui import RaceGui
from .fsm import RaceFsm


class RaceFacade(object):

    def attach_obs(self, meth):
        return self.event.attach(meth)

    def detach_obs(self, meth):
        return self.event.detach(meth)

    @property
    def results(self):
        return self.gui.results


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
            [('event', self.event_cls, [self, race_props.ingame_menu])]]
        GameObject.__init__(self, init_lst)


class RaceSinglePlayer(Race):
    logic_cls = RaceLogicSinglePlayer


class RaceServer(Race):
    logic_cls = RaceLogicServer
    event_cls = RaceEventServer


class RaceClient(Race):
    logic_cls = RaceLogicClient
    event_cls = RaceEventClient
