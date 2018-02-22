from yyagl.gameobject import GameObject
from yyagl.facade import Facade
from .logic import SeasonLogic


class SeasonProps(object):

    def __init__(
            self, gameprops, car_names, player_car_name, player_car_names,
            drivers, tuning_imgs, font, countdown_sfx, single_race, wpn2img,
            tuning_engine, tuning_tires, tuning_suspensions, race_start_time,
            countdown_seconds):
        self.gameprops = gameprops
        self.car_names = car_names
        self.player_car_name = player_car_name
        self.player_car_names = player_car_names
        self.drivers = drivers
        self.tuning_imgs = tuning_imgs
        self.font = font
        self.countdown_sfx = countdown_sfx
        self.single_race = single_race
        self.wpn2img = wpn2img
        self.tuning_engine = tuning_engine
        self.tuning_tires = tuning_tires
        self.tuning_suspensions = tuning_suspensions
        self.race_start_time = race_start_time
        self.countdown_seconds = countdown_seconds


class SeasonFacade(Facade):

    def __init__(self):
        self._fwd_mth('attach_obs', lambda obj: obj.logic.attach)
        self._fwd_mth('detach_obs', lambda obj: obj.logic.detach)
        self._fwd_mth('start', lambda obj: obj.logic.start)
        self._fwd_mth('load', lambda obj: obj.logic.load)
        self._fwd_mth('create_race_server', lambda obj: obj.logic.create_race_server)
        self._fwd_mth('create_race_client', lambda obj: obj.logic.create_race_client)
        self._fwd_mth('create_race', lambda obj: obj.logic.create_race)
        self._fwd_prop('ranking', lambda obj: obj.logic.ranking)
        self._fwd_prop('tuning', lambda obj: obj.logic.tuning)
        self._fwd_prop('props', lambda obj: obj.logic.props)
        self._fwd_prop('race', lambda obj: obj.logic.race)

    @property
    def drivers_skills(self):
        return self.logic.props.gameprops.drivers_skills

    @drivers_skills.setter
    def drivers_skills(self, val):
        self.logic.drivers_skills = val


class Season(GameObject, SeasonFacade):
    logic_cls = SeasonLogic

    def __init__(self, season_props):
        init_lst = [[('logic', self.logic_cls, [self, season_props])]]
        GameObject.__init__(self, init_lst)
        SeasonFacade.__init__(self)

    def destroy(self):
        GameObject.destroy(self)
        SeasonFacade.destroy(self)


class SingleRaceSeason(Season):
    pass
