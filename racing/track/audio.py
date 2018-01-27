from yyagl.gameobject import AudioColleague


class TrackAudio(AudioColleague):

    def __init__(self, mediator, music_fpath):
        AudioColleague.__init__(self, mediator)
        self.music = loader.loadSfx(music_fpath)
        self.music.set_loop(True)
