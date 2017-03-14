from yyagl.gameobject import GameObjectMdt, Ai, Audio
from .fsm import CarFsm
from .gfx import CarGfx, CarGfxProps
from .phys import CarPhys, CarPlayerPhys, CarPhysProps
from .event import CarEvent, CarPlayerEvent, CarPlayerEventServer, \
    CarPlayerEventClient, CarNetworkEvent, CarAiEvent
from .logic import CarLogic, CarPlayerLogic, CarLogicProps
from .audio import CarAudio, CarAudioProps
from .gui import CarGui, CarPlayerGui, CarGuiProps
from .ai import CarAi


class Car(GameObjectMdt):
    fsm_cls = CarFsm
    gfx_cls = CarGfx
    gui_cls = CarGui
    phys_cls = CarPhys
    event_cls = CarEvent
    logic_cls = CarLogic
    ai_cls = Ai
    audio_cls = Audio

    def __init__(
            self, name, coll_path, coll_name, pos, hpr, cb, race, laps, keys,
            joystick, sounds, color_main, color, font, car_path, phys_file,
            wheel_names, tuning_engine, tuning_tires, tuning_suspensions,
            road_name, model_name, damage_paths, wheel_gfx_names,
            particle_path, driver_engine, driver_tires, driver_suspensions,
            rocket_path, cam_vec, track_waypoints):
        eng.log_mgr.log('init car ' + name)  # two params: path and name
        self.pos = pos
        self.hpr = hpr
        #self.path = car_path + '/' + name
        self.name = name
        self.race = race
        self.laps = laps
        self.road_name = road_name
        gui_props = CarGuiProps(color_main, color, font, laps)
        audio_props = CarAudioProps(
            sounds['engine'], sounds['brake'], sounds['crash'],
            sounds['crash_hs'], sounds['lap'], sounds['landing'])
        carlogic_props = CarLogicProps(self.pos, self.hpr, cam_vec, joystick,
                                       track_waypoints)
        cargfx_props = CarGfxProps(model_name, damage_paths, wheel_gfx_names,
                                   particle_path)
        carphys_props = CarPhysProps(coll_path, coll_name, self.race.track.phys.model,
                 phys_file, wheel_names, tuning_engine, tuning_tires,
                 tuning_suspensions, driver_engine, driver_tires,
                 driver_suspensions)
        init_lst = [
            [('fsm', self.fsm_cls, [self])],
            [('gfx', self.gfx_cls, [self, cargfx_props]),
             ('phys', self.phys_cls, [self, carphys_props]),
             ('gui', self.gui_cls, [self, gui_props]),
             ('event', self.event_cls, [self, keys, joystick, rocket_path]),
             ('logic', self.logic_cls, [self, carlogic_props])],
            [('audio', self.audio_cls, [self, audio_props])],
            [('ai', self.ai_cls, [self, road_name])]]
        GameObjectMdt.__init__(self, init_lst, cb)

    def destroy(self):
        self.race = None
        GameObjectMdt.destroy(self)


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
