from yyagl.gameobject import GameObject, AiColleague, AudioColleague
from yyagl.facade import Facade
from .fsm import CarFsm
from .gfx import CarGfx, CarPlayerGfx
from .phys import CarPhys, CarPlayerPhys
from .event import CarEvent, CarPlayerEvent, CarPlayerEventServer, \
    CarPlayerEventClient, CarNetworkEvent, CarAiEvent, CarAiPlayerEvent
from .logic import CarLogic, CarPlayerLogic
from .audio import CarAudio, CarPlayerAudio
from .gui import CarGui, CarPlayerGui, CarNetworkGui
from .ai import CarAi


class CarProps(object):

    def __init__(
            self, race_props, name, pos, hpr, callback, race, driver_engine,
            driver_tires, driver_suspensions, track_waypoints, ai_poller):
        self.race_props = race_props
        self.name = name
        self.pos = pos
        self.hpr = hpr
        self.callback = callback
        self.race = race
        self.driver_engine = driver_engine
        self.driver_tires = driver_tires
        self.driver_suspensions = driver_suspensions
        self.track_waypoints = track_waypoints
        self.ai_poller = ai_poller


class CarFacade(Facade):

    def __init__(self):
        self._fwd_mth('last_wp_not_fork',
                           lambda obj: obj.logic.last_wp_not_fork)
        self._fwd_mth('not_fork_wps', lambda obj: obj.logic.not_fork_wps)
        self._fwd_mth('reparent', lambda obj: obj.gfx.reparent)
        self._fwd_mth('attach_obs', lambda obj: obj.event.attach)
        self._fwd_mth('detach_obs', lambda obj: obj.event.detach)
        self._fwd_mth('reset_car', lambda obj: obj.logic.reset_car)
        self._fwd_mth('start', lambda obj: obj.event.start)
        self._fwd_mth('get_pos', lambda obj: obj.gfx.nodepath.get_pos)
        self._fwd_mth('get_hpr', lambda obj: obj.gfx.nodepath.get_hpr)
        self._fwd_mth('closest_wp', lambda obj: obj.logic.closest_wp)
        self._fwd_mth('upd_ranking', lambda obj: obj.gui.upd_ranking)
        self._fwd_mth(
            'get_linear_velocity',
            lambda obj: obj.phys.vehicle.get_chassis().get_linear_velocity)
        self._fwd_mth('demand', lambda obj: obj.fsm.demand)
        self._fwd_prop('lap_times', lambda obj: obj.logic.lap_times)
        self._fwd_prop('path', lambda obj: obj.gfx.path)
        self._fwd_prop('laps_num', lambda obj: obj.logic.laps_num)
        self._fwd_prop('name', lambda obj: obj.logic.cprops.name)
        self._fwd_prop('laps', lambda obj: obj.logic.cprops.race_props.laps)
        self._fwd_prop('pos', lambda obj: obj.gfx.nodepath.get_pos())
        self._fwd_prop('heading', lambda obj: obj.gfx.nodepath.get_h())


class Car(GameObject, CarFacade):
    fsm_cls = CarFsm
    gfx_cls = CarGfx
    gui_cls = CarGui
    phys_cls = CarPhys
    event_cls = CarEvent
    logic_cls = CarLogic
    ai_cls = AiColleague
    audio_cls = CarAudio

    def __init__(self, car_props):
        self.eng.log_mgr.log('init car ' + car_props.name)
        init_lst = [
            [('fsm', self.fsm_cls, [self, car_props])],
            [('gfx', self.gfx_cls, [self, car_props]),
             ('phys', self.phys_cls, [self, car_props]),
             ('logic', self.logic_cls, [self, car_props]),
             ('gui', self.gui_cls, [self, car_props.race_props]),
             ('event', self.event_cls, [self, car_props.race_props]),
             ('ai', self.ai_cls, [self, car_props])],
            [('audio', self.audio_cls, [self, car_props.race_props])]]
        GameObject.__init__(self, init_lst, car_props.callback)
        CarFacade.__init__(self)

    def destroy(self):
        GameObject.destroy(self)
        CarFacade.destroy(self)


class CarPlayer(Car):
    event_cls = CarPlayerEvent
    audio_cls = CarPlayerAudio
    gui_cls = CarPlayerGui
    logic_cls = CarPlayerLogic
    phys_cls = CarPlayerPhys
    gfx_cls = CarPlayerGfx


class CarPlayerServer(Car):
    event_cls = CarPlayerEventServer
    audio_cls = CarPlayerAudio
    gui_cls = CarPlayerGui
    logic_cls = CarPlayerLogic


class CarPlayerClient(Car):
    event_cls = CarPlayerEventClient
    audio_cls = CarPlayerAudio
    gui_cls = CarPlayerGui
    logic_cls = CarPlayerLogic


class NetworkCar(Car):
    event_cls = CarNetworkEvent
    gui_cls = CarNetworkGui


class AiCar(Car):
    ai_cls = CarAi
    event_cls = CarAiEvent


class AiCarPlayer(AiCar, CarPlayer):
    event_cls = CarAiPlayerEvent
