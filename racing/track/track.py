from yyagl.gameobject import GameObject
from yyagl.facade import Facade
from .gfx import TrackGfx, TrackGfxShader
from .phys import TrackPhys, TrackPhysDebug
from .event import TrackEvent
from .audio import TrackAudio


class TrackFacade(Facade):

    def __init__(self):
        self._fwd_mth('get_start_pos', lambda obj: obj.phys.get_start_pos)
        self._fwd_mth('play_music', lambda obj: obj.audio.music.play)
        self._fwd_mth('stop_music', lambda obj: obj.audio.music.stop)
        self._fwd_mth('update', lambda obj: obj.event.update)
        self._fwd_mth('attach_obs', lambda obj: obj.event.attach)
        self._fwd_mth('detach_obs', lambda obj: obj.event.detach)
        self._fwd_mth('reparent_to', lambda obj: obj.gfx.model.reparent_to)
        self._fwd_prop('lrtb', lambda obj: obj.phys.lrtb)


class Track(GameObject, TrackFacade):

    def __init__(self, race_props):
        self.eng.log_mgr.log('init track')
        self.rprops = r_p = race_props
        gfx_cls = TrackGfxShader if r_p.shaders_dev else TrackGfx
        phys_cls = TrackPhysDebug if self.rprops.show_waypoints else TrackPhys
        init_lst = [
            [('phys', phys_cls, [self, r_p]),
             ('gfx', gfx_cls, [self, r_p])],
            [('event', TrackEvent, [self, r_p.shaders_dev, r_p.shadow_src])],
            [('audio', TrackAudio, [self, r_p.music_path])]]
        GameObject.__init__(self, init_lst, self.__on_track_loaded)
        TrackFacade.__init__(self)

    def __on_track_loaded(self):
        self.event.notify('on_track_loaded')

    def destroy(self):
        GameObject.destroy(self)
        TrackFacade.destroy(self)
