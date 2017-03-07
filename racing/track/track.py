from yyagl.gameobject import GameObjectMdt
from .gfx import TrackGfx
from .phys import TrackPhys
from .event import TrackEvent
from .audio import TrackAudio


class Track(GameObjectMdt):

    def __init__(
            self, path, cb, shaders, music_path, coll_path, unmerged, merged,
            ghosts, corner_names, waypoint_names, show_waypoints, weapons,
            weapon_names, start, name, track_path, model_name, empty_name,
            anim_name, omni_tag, thanks, sign_name, camera_vec, shadow_src,
            laps):
        eng.log_mgr.log('init track')  # facade
        self.path = path
        self.camera_vector = camera_vec
        self.shadow_source = shadow_src
        self.laps = laps
        init_lst = [
            [('phys', TrackPhys, [
                self, coll_path, unmerged, merged, ghosts, corner_names,
                waypoint_names, show_waypoints, weapons, weapon_names, start]),
             ('gfx', TrackGfx, [
                 self, name, track_path, model_name, empty_name, anim_name,
                 omni_tag, shaders, thanks, sign_name],
              lambda: self.gfx.attach(self.on_loading))],
            [('event', TrackEvent, [self, shaders])],
            [('audio', TrackAudio, [self, music_path])]]
        GameObjectMdt.__init__(self, init_lst, cb)

    def on_loading(self, txt):
        self.notify('on_loading', txt)
