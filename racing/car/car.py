from yyagl.gameobject import GameObject, Ai, Audio
from .fsm import CarFsm, CarFsmProps
from .gfx import CarGfx, CarGfxProps
from .phys import CarPhys, CarPlayerPhys, CarPhysProps
from .event import CarEvent, CarPlayerEvent, CarPlayerEventServer, \
    CarPlayerEventClient, CarNetworkEvent, CarAiEvent, CarEventProps, \
    CarAiPlayerEvent
from .logic import CarLogic, CarPlayerLogic, CarLogicProps
from .audio import CarAudio, CarAudioProps
from .gui import CarGui, CarPlayerGui, CarGuiProps
from .ai import CarAi


class CarProps(object):

    def __init__(
        self, name, coll_path, coll_name, pos, hpr, callback, race, laps, keys,
            joystick, sounds, color_main, color, font, car_path, phys_file,
            wheel_names, tuning_engine, tuning_tires, tuning_suspensions,
            road_name, model_name, damage_paths, wheel_gfx_names,
            particle_path, driver_engine, driver_tires, driver_suspensions,
            rocket_path, cam_vec, track_waypoints, respawn_name, pitstop_name,
            wall_name, goal_name, bonus_name, roads_names):
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
        self.cam_vec = cam_vec
        self.track_waypoints = track_waypoints
        self.respawn_name = respawn_name
        self.pitstop_name = pitstop_name
        self.wall_name = wall_name
        self.goal_name = goal_name
        self.bonus_name = bonus_name
        self.roads_names = roads_names


class CarFacade(object):

    def reparent(self):
        return self.gfx.reparent()

    def attach_obs(self, meth):
        return self.event.attach(meth)

    def detach_obs(self, meth):
        return self.event.detach(meth)

    def reset_car(self):
        return self.logic.reset_car()

    def start(self):
        return self.event.start()

    def get_pos(self):
        return self.gfx.nodepath.get_pos()

    def get_hpr(self):
        return self.gfx.nodepath.get_hpr()

    def closest_wp(self):
        return self.logic.closest_wp()

    @property
    def lap_times(self):
        return self.logic.lap_times

    def get_linear_velocity(self):
        return self.phys.vehicle.getChassis().getLinearVelocity()

    @property
    def path(self):
        return self.gfx.path

    def demand(self, state):
        return self.fsm.demand(state)


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
        eng.log_mgr.log('init car ' + car_props.name)
        self.name = car_props.name
        self.laps = car_props.laps
        self.road_name = car_props.road_name
        gui_props = CarGuiProps(
            car_props.color_main, car_props.color, car_props.font,
            car_props.laps)
        audio_props = CarAudioProps(
            car_props.sounds['engine'], car_props.sounds['brake'],
            car_props.sounds['crash'], car_props.sounds['crash_hs'],
            car_props.sounds['lap'], car_props.sounds['landing'])
        carlogic_props = CarLogicProps(
            car_props.pos, car_props.hpr, car_props.cam_vec,
            car_props.joystick, car_props.track_waypoints)
        cargfx_props = CarGfxProps(
            car_props.model_name, car_props.damage_paths,
            car_props.wheel_gfx_names, car_props.particle_path)
        carphys_props = CarPhysProps(
            car_props.coll_path, car_props.coll_name,
            car_props.race.track.phys.model, car_props.phys_file,
            car_props.wheel_names, car_props.tuning_engine,
            car_props.tuning_tires, car_props.tuning_suspensions,
            car_props.driver_engine, car_props.driver_tires,
            car_props.driver_suspensions)
        carfsm_props = CarFsmProps(car_props.road_name,
                                   car_props.track_waypoints)
        carevent_props = CarEventProps(
            car_props.keys, car_props.joystick, car_props.rocket_path,
            car_props.respawn_name, car_props.pitstop_name,
            car_props.road_name, car_props.wall_name, car_props.goal_name,
            car_props.bonus_name, car_props.roads_names)
        init_lst = [
            [('fsm', self.fsm_cls, [self, carfsm_props])],
            [('gfx', self.gfx_cls, [self, cargfx_props]),
             ('phys', self.phys_cls, [self, carphys_props]),
             ('gui', self.gui_cls, [self, gui_props]),
             ('event', self.event_cls, [self, carevent_props]),
             ('logic', self.logic_cls, [self, carlogic_props])],
            [('audio', self.audio_cls, [self, audio_props])],
            [('ai', self.ai_cls, [self, car_props.road_name,
                                  car_props.track_waypoints])]]
        GameObject.__init__(self, init_lst, car_props.callback)


class PlayerCar(Car):
    event_cls = CarPlayerEvent
    audio_cls = CarAudio
    gui_cls = CarPlayerGui
    logic_cls = CarPlayerLogic
    phys_cls = CarPlayerPhys


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
