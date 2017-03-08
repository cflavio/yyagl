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
            damage_paths, wheel_gfx_names, particle_path, drivers, shaders,
            music_path, coll_track_path, unmerged, merged, ghosts,
            corner_names, waypoint_names, show_waypoints, weapons,
            weapon_names, start, track_name, track_path, track_model_name,
            empty_name, anim_name, omni_tag, thanks, sign_name, minimap_path,
            minimap_image, col_dct, camera_vec, shadow_src, laps, rocket_path,
            bonus_name, bonus_suff):
        init_lst = [
            [('fsm', self.fsm_cls, [self])],
            [('gui', self.gui_cls, [self, track_name, minimap_path,
                                    minimap_image, col_dct, font])],
            [('logic', self.logic_cls, [
                self, keys, joystick, sounds, color_main, color, font,
                coll_path, coll_name, car_path, phys_file, wheel_names,
                tuning_engine, tuning_tires, tuning_suspensions, road_name,
                base_path, model_name, damage_paths, wheel_gfx_names,
                particle_path, drivers, shaders, music_path, coll_track_path,
                unmerged, merged, ghosts, corner_names, waypoint_names,
                show_waypoints, weapons, weapon_names, start, track_name,
                track_path, track_model_name, empty_name, anim_name, omni_tag,
                thanks, sign_name, camera_vec, shadow_src, laps,
                rocket_path, bonus_name, bonus_suff])],
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
