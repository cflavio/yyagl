from yyagl.gameobject import GameObject
from yyagl.engine.log import LogMgr
from .gfx import TrackGfx
from .phys import TrackPhys
from .event import TrackEvent
from .audio import TrackAudio


class TrackFacade(object):

    def get_start_pos(self, idx):
        return self.phys.get_start_pos(idx)

    def play_music(self):
        return self.audio.music.play()

    def stop_music(self):
        return self.audio.music.stop()

    def update(self, player_pos):
        return self.event.update(player_pos)

    def attach_obs(self, meth):
        return self.event.attach(meth)

    def detach_obs(self, meth):
        return self.event.detach(meth)

    @property
    def lrtb(self):
        return self.phys.lrtb


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

    def __on_track_loaded(self):
        self.event.notify('on_track_loaded')