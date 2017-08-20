from collections import namedtuple
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


__fields = 'name pos hpr callback race driver_engine driver_tires ' + \
    'driver_suspensions track_waypoints'


CarProps = namedtuple('CarProps', __fields)


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
        self._fwd_prop_lazy('name', lambda: self.logic.cprops.name)
        self._fwd_prop_lazy('laps', lambda: self.logic.rprops.laps)
        self._fwd_prop_lazy('pos', lambda: self.gfx.nodepath.get_pos())


class Car(GameObject, CarFacade):
    fsm_cls = CarFsm
    gfx_cls = CarGfx
    gui_cls = CarGui
    phys_cls = CarPhys
    event_cls = CarEvent
    logic_cls = CarLogic
    ai_cls = Ai
    audio_cls = Audio

    def __init__(self, car_props, race_props):
        LogMgr().log('init car ' + car_props.name)
        #self.name = car_props.name
        #self.laps = race_props.laps
        #self.road_name = race_props.road_name
        init_lst = [
            [('fsm', self.fsm_cls, [self, car_props, race_props])],
            [('gfx', self.gfx_cls, [self, car_props, race_props]),
             ('phys', self.phys_cls, [self, car_props, race_props]),
             ('logic', self.logic_cls, [self, car_props, race_props]),
             ('gui', self.gui_cls, [self, race_props]),
             ('event', self.event_cls, [self, race_props]),
             ('ai', self.ai_cls, [self, car_props, race_props])],
            [('audio', self.audio_cls, [self, race_props])]]
        GameObject.__init__(self, init_lst, car_props.callback)
        CarFacade.__init__(self)


class CarPlayer(Car):
    event_cls = CarPlayerEvent
    audio_cls = CarAudio
    gui_cls = CarPlayerGui
    logic_cls = CarPlayerLogic
    phys_cls = CarPlayerPhys
    gfx_cls = CarPlayerGfx


class CarPlayerServer(Car):
    event_cls = CarPlayerEventServer
    audio_cls = CarAudio
    gui_cls = CarGui
    logic_cls = CarPlayerLogic


class CarPlayerClient(Car):
    event_cls = CarPlayerEventClient
    audio_cls = CarAudio
    gui_cls = CarGui
    logic_cls = CarPlayerLogic


class NetworkCar(Car):
    event_cls = CarNetworkEvent


class AiCar(Car):
    ai_cls = CarAi
    event_cls = CarAiEvent


class AiCarPlayer(AiCar, CarPlayer):
    event_cls = CarAiPlayerEvent
