from yyagl.gameobject import GameObjectMdt, Ai, Gui, Audio
from .fsm import CarFsm
from .gfx import CarGfx
from .phys import CarPhys, CarPlayerPhys
from .event import CarEvent, CarPlayerEvent, CarPlayerEventServer, \
    CarPlayerEventClient, CarNetworkEvent, CarAiEvent
from .logic import CarLogic, CarPlayerLogic
from .audio import CarAudio
from .gui import CarGui
from .ai import CarAi


class Car(GameObjectMdt):
    fsm_cls = CarFsm
    gfx_cls = CarGfx
    gui_cls = Gui
    phys_cls = CarPhys
    event_cls = CarEvent
    logic_cls = CarLogic
    ai_cls = Ai
    audio_cls = Audio

    def __init__(self, path, pos, hpr, cb, race, laps, keys, joystick, sounds):
        eng.log_mgr.log('init car')
        self.pos = pos
        self.hpr = hpr
        self.path = path
        self.race = race
        self.laps = laps
        init_lst = [
            [('fsm', self.fsm_cls, [self])],
            [('gfx', self.gfx_cls, [self, self.path]),
             ('phys', self.phys_cls, [self, self.path,
                                      self.race.track.phys.model]),
             ('gui', self.gui_cls, [self]),
             ('event', self.event_cls, [self, keys, joystick]),
             ('logic', self.logic_cls, [self, self.pos, self.hpr])],
            [('audio', self.audio_cls, [self, sounds])],
            [('ai', self.ai_cls, [self])]]
        GameObjectMdt.__init__(self, init_lst, cb)

    def destroy(self):
        self.race = None
        GameObjectMdt.destroy(self)


class PlayerCar(Car):
    event_cls = CarPlayerEvent
    audio_cls = CarAudio
    gui_cls = CarGui
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
