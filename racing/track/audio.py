from yyagl.gameobject import Audio


class TrackAudio(Audio):

    def __init__(self, mdt, music_fpath):
        Audio.__init__(self, mdt)
        self.music = loader.loadSfx(music_fpath)
        self.music.set_loop(True)
