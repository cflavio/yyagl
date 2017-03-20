from abc import ABCMeta
from yyagl.gameobject import GameObjectMdt
from .logic import RaceLogic, RaceLogicSinglePlayer, RaceLogicServer, \
    RaceLogicClient, RaceLogicProps
from .event import RaceEvent, RaceEventServer, RaceEventClient
from .gui.gui import RaceGui, RaceGuiProps
from .fsm import RaceFsm


class RaceFacade(object):

    def attach_obs(self, meth):
        return self.event.attach(meth)

    def detach_obs(self, meth):
        return self.event.detach(meth)

    @property
    def results(self):
        return self.gui.results


class Race(GameObjectMdt, RaceFacade):
    __metaclass__ = ABCMeta
    logic_cls = RaceLogic
    event_cls = RaceEvent

    def __init__(self, race_props):
        r_p = race_props
        racelogic_props = RaceLogicProps(
            r_p.shaders, r_p.music_path, r_p.coll_track_path, r_p.unmerged,
            r_p.merged, r_p.ghosts, r_p.corner_names, r_p.waypoint_names,
            r_p.show_waypoints, r_p.weapons, r_p.weapon_names, r_p.start,
            r_p.track_name, r_p.track_path, r_p.track_model_name,
            r_p.empty_name, r_p.anim_name, r_p.omni_tag, r_p.sign_cb,
            r_p.sign_name, r_p.camera_vec, r_p.shadow_src, r_p.laps,
            r_p.bonus_model, r_p.bonus_suff, r_p.cars, r_p.a_i, r_p.drivers,
            r_p.coll_path, r_p.coll_name, r_p.keys, r_p.joystick, r_p.sounds,
            r_p.color_main, r_p.color, r_p.font, r_p.car_path, r_p.phys_file,
            r_p.wheel_names, r_p.tuning_engine, r_p.tuning_tires,
            r_p.tuning_suspensions, r_p.road_name, r_p.model_name,
            r_p.damage_paths, r_p.wheel_gfx_names, r_p.particle_path,
            r_p.rocket_path, r_p.respawn_name, r_p.pitstop_name, r_p.wall_name,
            r_p.goal_name, r_p.bonus_name, r_p.roads_names, r_p.grid)
        racegui_props = RaceGuiProps(
            r_p.minimap_path, r_p.minimap_image, r_p.col_dct, r_p.font,
            r_p.cars, r_p.menu_args, r_p.drivers_img, r_p.cars_imgs,
            r_p.share_urls, r_p.share_imgs, r_p.track_name,
            r_p.player_car_name)
        init_lst = [
            [('fsm', RaceFsm, [self, race_props.shaders])],
            [('gui', RaceGui, [self, racegui_props])],
            [('logic', self.logic_cls, [self, racelogic_props])],
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
