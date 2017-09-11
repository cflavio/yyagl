from collections import namedtuple
from yyagl.gameobject import GameObject
from yyagl.facade import Facade
from .logic import SeasonLogic

sp_attrs = 'gameprops car_names player_car_name drivers ' + \
    'tuning_imgs font countdown_sfx single_race ' + \
    'wpn2img tuning_engine tuning_tires tuning_suspensions ' + \
    'race_start_time countdown_seconds'
SeasonProps = namedtuple('SeasonProps', sp_attrs)


class SeasonFacade(Facade):

    def __init__(self):
        self._fwd_mth('attach_obs', self.logic.attach)
        self._fwd_mth('detach_obs', self.logic.detach)
        self._fwd_mth('start', self.logic.start)
        self._fwd_mth('load', self.logic.load)
        self._fwd_mth('create_race_server', self.logic.create_race_server)
        self._fwd_mth('create_race_client', self.logic.create_race_client)
        self._fwd_mth('create_race', self.logic.create_race)
        self._fwd_prop('ranking', self.logic.ranking)
        self._fwd_prop('tuning', self.logic.tuning)
        self._fwd_prop_lazy('props', lambda obj: obj.logic.props)
        self._fwd_prop_lazy('race', lambda obj: obj.logic.race)

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


class SingleRaceSeason(Season):
    pass
