from yyagl.gameobject import AudioColleague


class TrackAudio(AudioColleague):

    def __init__(self, mdt, music_fpath):
        AudioColleague.__init__(self, mdt)
        self.music = loader.loadSfx(music_fpath)
        self.music.set_loop(True)
