from logging import info
from yyagl.gameobject import GameObject
from yyagl.facade import Facade
from .gfx import TrackGfx, TrackGfxShader, TrackGfxDebug
from .phys import TrackPhys
from .audio import TrackAudio


class TrackFacade(Facade):

    def __init__(self):
        prop_lst = [('bounds', lambda obj: obj.phys.bounds)]
        mth_lst = [
            ('get_start_pos_hpr', lambda obj: obj.phys.get_start_pos_hpr),
            ('play_music', lambda obj: obj.audio.music.play),
            ('stop_music', lambda obj: obj.audio.music.stop),
            ('update', lambda obj: obj.event.update),
            ('attach_obs', lambda obj: obj.attach),
            ('detach_obs', lambda obj: obj.detach),
            ('reparent_to', lambda obj: obj.gfx.model.reparent_to)]
        Facade.__init__(self, prop_lst, mth_lst)


class Track(GameObject, TrackFacade):

    def __init__(self, race_props):
        info('init track')
        self.race_props = self.__rpr = race_props
        self.__gfx_cls = TrackGfxShader if self.__rpr.shaders_dev else TrackGfx
        self.__gfx_cls = TrackGfxDebug if self.__rpr.show_waypoints else self.__gfx_cls
        GameObject.__init__(self)
        taskMgr.add(self.__build_comps())
        TrackFacade.__init__(self)

    async def __build_comps(self):
        gfx_task = taskMgr.add(self.__build_gfx)
        await gfx_task
        self.phys = TrackPhys(self, self.__rpr)
        self.audio = TrackAudio(self, self.__rpr.music_path)
        self.notify('on_track_loaded')

    def __build_gfx(self, task):
        self.gfx = self.__gfx_cls(self, self.__rpr)

    def destroy(self):
        self.gfx.destroy()
        self.phys.destroy()
        self.audio.destroy()
        GameObject.destroy(self)
        TrackFacade.destroy(self)
