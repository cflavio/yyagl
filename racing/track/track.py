from yyagl.gameobject import GameObject
from yyagl.facade import Facade
from .gfx import TrackGfx, TrackGfxShader
from .phys import TrackPhys, TrackPhysDebug
from .audio import TrackAudio


class TrackFacade(Facade):

    def __init__(self):
        self._fwd_mth('get_start_pos', lambda obj: obj.phys.get_start_pos)
        self._fwd_mth('play_music', lambda obj: obj.audio.music.play)
        self._fwd_mth('stop_music', lambda obj: obj.audio.music.stop)
        self._fwd_mth('update', lambda obj: obj.event.update)
        self._fwd_mth('attach_obs', lambda obj: obj.attach)
        self._fwd_mth('detach_obs', lambda obj: obj.detach)
        self._fwd_mth('reparent_to', lambda obj: obj.gfx.model.reparent_to)
        self._fwd_prop('bounds', lambda obj: obj.phys.lrtb)


class Track(GameObject, TrackFacade):

    def __init__(self, race_props):
        self.eng.log_mgr.log('init track')
        self.race_props = rpr = race_props
        gfx_cls = TrackGfxShader if rpr.shaders_dev else TrackGfx
        phys_cls = TrackPhysDebug if self.race_props.show_waypoints else TrackPhys
        init_lst = [
            [('phys', phys_cls, [self, rpr]),
             ('gfx', gfx_cls, [self, rpr])],
            [('audio', TrackAudio, [self, rpr.music_path])]]
        GameObject.__init__(self, init_lst, self.__on_track_loaded)
        TrackFacade.__init__(self)

    def __on_track_loaded(self): self.notify('on_track_loaded')

    def destroy(self):
        GameObject.destroy(self)
        TrackFacade.destroy(self)
