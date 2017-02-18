from yyagl.gameobject import Audio
import yaml


class TrackAudio(Audio):

    def __init__(self, mdt):
        Audio.__init__(self, mdt)
        with open('assets/models/%s/track.yml' % self.mdt.path) as track_file:
            track_conf = yaml.load(track_file)
            music_name = track_conf['music']
        self.music = loader.loadSfx('assets/music/%s.ogg' % music_name)
        self.music.set_loop(True)
