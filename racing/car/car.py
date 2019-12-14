from logging import info
from yyagl.gameobject import GameObject, AiColleague
from yyagl.facade import Facade
from .fsm import CarFsm, CarPlayerFsm
from .gfx import CarGfx, CarPlayerGfx, CarNetworkGfx
from .phys import CarPhys, CarPlayerPhys
from .event import CarEvent, CarPlayerEvent, CarPlayerEventServer, \
    CarPlayerEventClient, CarNetworkEvent, CarAiEvent, CarAiPlayerEvent
from .logic import CarLogic, CarPlayerLogic
from .audio import CarAudio, CarPlayerAudio
from .gui import CarGui, CarPlayerGui, CarPlayerLocalMPGui, \
    CarPlayerMPGui, CarNetworkGui
from .ai import CarAi


class CarProps(object):

    def __init__(
            self, race_props, name, pos, hpr, callback, race, driver_engine,
            driver_tires, driver_suspensions, track_waypoints, track_skidmark_col, ai_poller):
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
        self.track_skidmark_col = track_skidmark_col
        self.ai_poller = ai_poller


class CarFacade(Facade):

    def __init__(self):
        prop_lst = [
            ('lap_times', lambda obj: obj.logic.lap_times),
            ('path', lambda obj: obj.gfx.path),
            ('laps_num', lambda obj: obj.logic.laps_num),
            ('name', lambda obj: obj.logic.cprops.name),
            ('laps', lambda obj: obj.logic.cprops.race_props.laps),
            ('pos', lambda obj: obj.gfx.nodepath.get_pos()),
            ('heading', lambda obj: obj.gfx.nodepath.h)]
        mth_lst = [
            ('last_wp_not_fork', lambda obj: obj.logic.last_wp_not_fork),
            ('not_fork_wps', lambda obj: obj.logic.not_fork_wps),
            ('reparent', lambda obj: obj.gfx.reparent),
            ('attach_obs', lambda obj: obj.event.attach),
            ('detach_obs', lambda obj: obj.event.detach),
            ('reset_car', lambda obj: obj.logic.reset_car),
            ('start', lambda obj: obj.event.start),
            ('get_pos', lambda obj: obj.gfx.nodepath.get_pos),
            ('get_hpr', lambda obj: obj.gfx.nodepath.get_hpr),
            ('closest_wp', lambda obj: obj.logic.closest_wp),
            ('upd_ranking', lambda obj: obj.gui.upd_ranking),
            ('get_linear_velocity', lambda obj: obj.phys.vehicle.get_chassis().get_linear_velocity),
            ('demand', lambda obj: obj.fsm.demand)]
        Facade.__init__(self, prop_lst, mth_lst)


class Car(GameObject, CarFacade):
    fsm_cls = CarFsm
    gfx_cls = CarGfx
    gui_cls = CarGui
    phys_cls = CarPhys
    event_cls = CarEvent
    logic_cls = CarLogic
    ai_cls = AiColleague
    audio_cls = CarAudio

    def __init__(self, car_props, player_car_idx, tuning, players):
        info('init car ' + car_props.name)
        self.player_car_idx = player_car_idx
        self.__tuning = tuning
        self._car_props = car_props
        self.__players = players
        GameObject.__init__(self)
        taskMgr.add(self.__build_comps())

    async def __build_comps(self):
        self.fsm = self.fsm_cls(self, self._car_props, self.__players)
        gfx_task = taskMgr.add(self.__build_gfx)
        await gfx_task
        self.phys = self.phys_cls(self, self._car_props, self.__tuning, self.__players)
        self.gfx.set_emitters()
        self.logic = self.logic_cls(self, self._car_props, self.__players)
        self.gui = self.gui_cls(self, self._car_props, self.__players)
        self.event = self.event_cls(self, self._car_props.race_props, self.__players)
        self.ai = self.ai_cls(self, self._car_props, self.__players)
        self.audio = self.audio_cls(self, self._car_props.race_props)
        CarFacade.__init__(self)
        self._car_props.callback()

    def __build_gfx(self, task):
        self.gfx = self.gfx_cls(self, self._car_props)

    def destroy(self):
        self.fsm.destroy()
        self.gfx.destroy()
        self.phys.destroy()
        self.logic.destroy()
        self.gui.destroy()
        self.event.destroy()
        self.ai.destroy()
        self.audio.destroy()
        GameObject.destroy(self)
        CarFacade.destroy(self)


class CarPlayer(Car):
    event_cls = CarPlayerEvent
    audio_cls = CarPlayerAudio
    gui_cls = CarPlayerGui
    logic_cls = CarPlayerLogic
    phys_cls = CarPlayerPhys
    gfx_cls = CarPlayerGfx
    fsm_cls = CarPlayerFsm


class CarPlayerServer(Car):
    event_cls = CarPlayerEventServer
    audio_cls = CarPlayerAudio
    gui_cls = CarPlayerMPGui
    logic_cls = CarPlayerLogic


class CarPlayerClient(Car):
    event_cls = CarPlayerEventClient
    audio_cls = CarPlayerAudio
    gui_cls = CarPlayerMPGui
    logic_cls = CarPlayerLogic


class CarPlayerLocalMP(CarPlayer):
    gui_cls = CarPlayerLocalMPGui


class NetworkCar(Car):
    gfx_cls = CarNetworkGfx
    event_cls = CarNetworkEvent
    gui_cls = CarNetworkGui


class AiCar(Car):
    ai_cls = CarAi
    event_cls = CarAiEvent


class AiCarPlayer(AiCar, CarPlayer):
    event_cls = CarAiPlayerEvent
