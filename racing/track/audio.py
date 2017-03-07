from yyagl.gameobject import Audio


class TrackAudio(Audio):

    def __init__(self, mdt, music_path):
        Audio.__init__(self, mdt)
        self.music = loader.loadSfx(music_path)
        self.music.set_loop(True)
