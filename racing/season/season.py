from yyagl.gameobject import GameObject
from yyagl.facade import Facade
from .logic import SeasonLogic


class SeasonProps(object):

    def __init__(
            self, gameprops, car_names, player_car_name, player_car_names,
            drivers, tuning_imgs, font, countdown_sfx, single_race, wpn2img,
            tuning_engine, tuning_tires, tuning_suspensions, race_start_time,
            countdown_seconds, camera, kind, room=None):
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
        self.camera = camera
        self.kind = kind
        self.room = room


class SeasonFacade(Facade):

    def __init__(self):
        prop_lst = [
            ('ranking', lambda obj: obj.logic.ranking),
            ('tuning', lambda obj: obj.logic.tuning),
            ('props', lambda obj: obj.logic.props),
            ('race', lambda obj: obj.logic.race)]
        mth_lst = [
            ('attach_obs', lambda obj: obj.logic.attach),
            ('detach_obs', lambda obj: obj.logic.detach),
            ('start', lambda obj: obj.logic.start),
            ('load', lambda obj: obj.logic.load),
            ('create_race_server', lambda obj: obj.logic.create_race_server),
            ('create_race_client', lambda obj: obj.logic.create_race_client),
            ('create_race', lambda obj: obj.logic.create_race)]
        Facade.__init__(self, prop_lst, mth_lst)

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
