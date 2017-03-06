from abc import ABCMeta
from yyagl.gameobject import GameObjectMdt
from .logic import RaceLogic, RaceLogicSinglePlayer, RaceLogicServer, \
    RaceLogicClient
from .event import RaceEvent, RaceEventServer, RaceEventClient
from .gui.gui import RaceGui
from .fsm import _Fsm


class Race(GameObjectMdt):
    __metaclass__ = ABCMeta
    logic_cls = RaceLogic
    event_cls = RaceEvent
    gui_cls = RaceGui
    fsm_cls = _Fsm

    def __init__(
            self, keys, joystick, sounds, color_main, color, font, coll_path,
            coll_name, car_path, phys_file, wheel_names, tuning_engine,
            tuning_tires, tuning_suspensions, road_name, base_path, model_name,
            damage_paths, wheel_gfx_names, particle_path, driver_engine,
            driver_tires, driver_suspensions):
        # tuning and driver's props should be managed from the game
        init_lst = [
            [('fsm', self.fsm_cls, [self])],
            [('gui', self.gui_cls, [self])],
            [('logic', self.logic_cls, [
                self, keys, joystick, sounds, color_main, color, font,
                coll_path, coll_name, car_path, phys_file, wheel_names,
                tuning_engine, tuning_tires, tuning_suspensions, road_name,
                base_path, model_name, damage_paths, wheel_gfx_names,
                particle_path, driver_engine, driver_tires,
                driver_suspensions])],
            [('event', self.event_cls, [self])]]
        GameObjectMdt.__init__(self, init_lst)


class RaceSinglePlayer(Race):
    logic_cls = RaceLogicSinglePlayer


class RaceServer(Race):
    logic_cls = RaceLogicServer
    event_cls = RaceEventServer


class RaceClient(Race):
    logic_cls = RaceLogicClient
    event_cls = RaceEventClient
