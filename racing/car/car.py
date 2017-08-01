from yyagl.gameobject import GameObject, Ai, Audio
from yyagl.engine.log import LogMgr
from yyagl.facade import Facade
from .fsm import CarFsm
from .gfx import CarGfx, CarPlayerGfx
from .phys import CarPhys, CarPlayerPhys
from .event import CarEvent, CarPlayerEvent, CarPlayerEventServer, \
    CarPlayerEventClient, CarNetworkEvent, CarAiEvent, CarAiPlayerEvent
from .logic import CarLogic, CarPlayerLogic
from .audio import CarAudio
from .gui import CarGui, CarPlayerGui
from .ai import CarAi


class CarProps(object):

    def __init__(
            self, name, coll_path, coll_name, pos, hpr, callback, race, laps,
            keys, joystick, sounds, color_main, color, font, car_path,
            phys_file, wheel_names, tuning_engine, tuning_tires,
            tuning_suspensions, road_name, model_name, damage_paths,
            wheel_gfx_names, particle_path, driver_engine, driver_tires,
            driver_suspensions, rocket_path, turbo_path, rotate_all_path,
            mine_path, cam_vec, track_waypoints, respawn_name, pitstop_name,
            wall_name, goal_name, bonus_name, roads_names, car_names):
        self.name = name
        self.coll_path = coll_path
        self.coll_name = coll_name
        self.pos = pos
        self.hpr = hpr
        self.callback = callback
        self.race = race
        self.laps = laps
        self.keys = keys
        self.joystick = joystick
        self.sounds = sounds
        self.color_main = color_main
        self.color = color
        self.font = font
        self.car_path = car_path
        self.phys_file = phys_file
        self.wheel_names = wheel_names
        self.tuning_engine = tuning_engine
        self.tuning_tires = tuning_tires
        self.tuning_suspensions = tuning_suspensions
        self.road_name = road_name
        self.model_name = model_name
        self.damage_paths = damage_paths
        self.wheel_gfx_names = wheel_gfx_names
        self.particle_path = particle_path
        self.driver_engine = driver_engine
        self.driver_tires = driver_tires
        self.driver_suspensions = driver_suspensions
        self.rocket_path = rocket_path
        self.turbo_path = turbo_path
        self.rotate_all_path = rotate_all_path
        self.mine_path = mine_path
        self.cam_vec = cam_vec
        self.track_waypoints = track_waypoints
        self.respawn_name = respawn_name
        self.pitstop_name = pitstop_name
        self.wall_name = wall_name
        self.goal_name = goal_name
        self.bonus_name = bonus_name
        self.roads_names = roads_names
        self.car_names = car_names


class CarFacade(Facade):

    def __init__(self):
        self._fwd_mth_lazy('last_wp_not_fork', lambda: self.logic.last_wp_not_fork)
        self._fwd_mth_lazy('not_fork_wps', lambda: self.logic.not_fork_wps)
        self._fwd_mth_lazy('reparent', lambda: self.gfx.reparent)
        self._fwd_mth_lazy('attach_obs', lambda: self.event.attach)
        self._fwd_mth_lazy('detach_obs', lambda: self.event.detach)
        self._fwd_mth_lazy('reset_car', lambda: self.logic.reset_car)
        self._fwd_mth_lazy('start', lambda: self.event.start)
        self._fwd_mth_lazy('get_pos', lambda: self.gfx.nodepath.get_pos)
        self._fwd_mth_lazy('get_hpr', lambda: self.gfx.nodepath.get_hpr)
        self._fwd_mth_lazy('closest_wp', lambda: self.logic.closest_wp)
        self._fwd_mth_lazy('get_linear_velocity', lambda: self.phys.vehicle.getChassis().getLinearVelocity)
        self._fwd_mth_lazy('demand', lambda: self.fsm.demand)
        self._fwd_prop_lazy('lap_times', lambda: self.logic.lap_times)
        self._fwd_prop_lazy('path', lambda: self.gfx.path)
        self._fwd_prop_lazy('laps_num', lambda: self.logic.laps_num)


class Car(GameObject, CarFacade):
    fsm_cls = CarFsm
    gfx_cls = CarGfx
    gui_cls = CarGui
    phys_cls = CarPhys
    event_cls = CarEvent
    logic_cls = CarLogic
    ai_cls = Ai
    audio_cls = Audio

    def __init__(self, car_props):
        LogMgr().log('init car ' + car_props.name)
        self.name = car_props.name
        self.laps = car_props.laps
        self.road_name = car_props.road_name
        init_lst = [
            [('fsm', self.fsm_cls, [self, car_props])],
            [('gfx', self.gfx_cls, [self, car_props]),
             ('phys', self.phys_cls, [self, car_props]),
             ('logic', self.logic_cls, [self, car_props]),
             ('gui', self.gui_cls, [self, car_props]),
             ('event', self.event_cls, [self, car_props]),
             ('ai', self.ai_cls, [self, car_props.road_name,
                                  car_props.track_waypoints,
                                  car_props.car_names])],
            [('audio', self.audio_cls, [self, car_props])]]
        GameObject.__init__(self, init_lst, car_props.callback)
        CarFacade.__init__(self)


class PlayerCar(Car):
    event_cls = CarPlayerEvent
    audio_cls = CarAudio
    gui_cls = CarPlayerGui
    logic_cls = CarPlayerLogic
    phys_cls = CarPlayerPhys
    gfx_cls = CarPlayerGfx


class PlayerCarServer(Car):
    event_cls = CarPlayerEventServer
    audio_cls = CarAudio
    gui_cls = CarGui
    logic_cls = CarPlayerLogic


class PlayerCarClient(Car):
    event_cls = CarPlayerEventClient
    audio_cls = CarAudio
    gui_cls = CarGui
    logic_cls = CarPlayerLogic


class NetworkCar(Car):
    event_cls = CarNetworkEvent


class AiCar(Car):
    ai_cls = CarAi
    event_cls = CarAiEvent


class AiPlayerCar(AiCar, PlayerCar):
    event_cls = CarAiPlayerEvent
