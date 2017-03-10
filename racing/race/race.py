from abc import ABCMeta
from yyagl.gameobject import GameObjectMdt
from .logic import RaceLogic, RaceLogicSinglePlayer, RaceLogicServer, \
    RaceLogicClient
from .event import RaceEvent, RaceEventServer, RaceEventClient
from .gui.gui import RaceGui
from .fsm import RaceFsm


class Race(GameObjectMdt):
    __metaclass__ = ABCMeta
    logic_cls = RaceLogic
    event_cls = RaceEvent

    def __init__(self, race_props):
        r_p = race_props
        init_lst = [
            [('fsm', RaceFsm, [self, race_props.shaders])],
            [('gui', RaceGui, [
                self, r_p.minimap_path, r_p.minimap_image, r_p.col_dct,
                r_p.font, r_p.cars, r_p.menu_args, r_p.drivers_img,
                r_p.cars_imgs, r_p.share_urls, r_p.share_imgs])],
            [('logic', self.logic_cls, [self, race_props])],
            [('event', self.event_cls, [self, race_props.ingame_menu])]]
        GameObjectMdt.__init__(self, init_lst)


class RaceSinglePlayer(Race):
    logic_cls = RaceLogicSinglePlayer


class RaceServer(Race):
    logic_cls = RaceLogicServer
    event_cls = RaceEventServer


class RaceClient(Race):
    logic_cls = RaceLogicClient
    event_cls = RaceEventClient
