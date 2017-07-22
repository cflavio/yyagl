from yyagl.gameobject import GameObject
from yyagl.engine.log import LogMgr
from yyagl.facade import Facade
from .gfx import TrackGfx
from .phys import TrackPhys
from .event import TrackEvent
from .audio import TrackAudio


class TrackFacade(Facade):

    def __init__(self):
        self._fwd_mth('get_start_pos', self.phys.get_start_pos)
        self._fwd_mth('play_music', self.audio.music.play)
        self._fwd_mth('stop_music', self.audio.music.stop)
        self._fwd_mth('update', self.event.update)
        self._fwd_mth('attach_obs', self.event.attach)
        self._fwd_mth('detach_obs', self.event.detach)
        self._fwd_prop('lrtb', self.phys.lrtb)


class Track(GameObject, TrackFacade):

    def __init__(self, race_props):
        LogMgr().log('init track')
        self.rprops = r_p = race_props
        init_lst = [
            [('phys', TrackPhys, [self, r_p]),
             ('gfx', TrackGfx, [self, r_p])],
            [('event', TrackEvent, [self, r_p.shaders_dev, r_p.shadow_src])],
            [('audio', TrackAudio, [self, r_p.music_path])]]
        GameObject.__init__(self, init_lst, self.__on_track_loaded)
        TrackFacade.__init__(self)

    def __on_track_loaded(self):
        self.event.notify('on_track_loaded')