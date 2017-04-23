from yyagl.gameobject import GameObject
from .gfx import TrackGfx, TrackGfxProps
from .phys import TrackPhys, TrackPhysProps
from .event import TrackEvent
from .audio import TrackAudio


class TrackProps(object):

    def __init__(
            self, path, callback, shaders, music_path, coll_path, unmerged,
            merged, ghosts, corner_names, waypoint_names, show_waypoints,
            weapons, weapon_names, start, name, track_path, model_name,
            empty_name, anim_name, omni_tag, sign_cb, sign_name, camera_vec,
            shadow_src, laps, bonus_model, bonus_suff):
        self.path = path
        self.callback = callback
        self.shaders = shaders
        self.music_path = music_path
        self.coll_path = coll_path
        self.unmerged = unmerged
        self.merged = merged
        self.ghosts = ghosts
        self.corner_names = corner_names
        self.waypoint_names = waypoint_names
        self.show_waypoints = show_waypoints
        self.weapons = weapons
        self.weapon_names = weapon_names
        self.start = start
        self.name = name
        self.track_path = track_path
        self.model_name = model_name
        self.empty_name = empty_name
        self.anim_name = anim_name
        self.omni_tag = omni_tag
        self.sign_cb = sign_cb
        self.sign_name = sign_name
        self.camera_vec = camera_vec
        self.shadow_src = shadow_src
        self.laps = laps
        self.bonus_model = bonus_model
        self.bonus_suff = bonus_suff


class TrackFacade(object):

    def get_start_pos(self, idx):
        return self.phys.get_start_pos(idx)

    def play_music(self):
        return self.audio.music.play()

    def stop_music(self):
        return self.audio.music.stop()

    def update(self, player_pos):
        return self.event.update(player_pos)

    @property
    def lrtb(self):
        return self.phys.lrtb


class Track(GameObject, TrackFacade):

    def __init__(self, track_props):
        eng.log('init track')
        self.props = t_p = track_props
        trackphys_props = TrackPhysProps(
            t_p.coll_path, t_p.unmerged, t_p.merged, t_p.ghosts,
            t_p.corner_names, t_p.waypoint_names, t_p.show_waypoints,
            t_p.weapons, t_p.weapon_names, t_p.start, t_p.bonus_model,
            t_p.bonus_suff)
        trackgfx_props = TrackGfxProps(
            t_p.name, t_p.track_path, t_p.model_name, t_p.empty_name,
            t_p.anim_name, t_p.omni_tag, t_p.shaders, t_p.sign_cb,
            t_p.sign_name, t_p.shadow_src)
        init_lst = [
            [('phys', TrackPhys, [self, trackphys_props]),
             ('gfx', TrackGfx, [self, trackgfx_props])],
            [('event', TrackEvent, [self, t_p.shaders, t_p.shadow_src])],
            [('audio', TrackAudio, [self, t_p.music_path])]]
        GameObject.__init__(self, init_lst, t_p.callback)
