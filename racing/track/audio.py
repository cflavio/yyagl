from yyagl.gameobject import AudioColleague


class TrackAudio(AudioColleague):

    def __init__(self, mediator, music_fpath):
        AudioColleague.__init__(self, mediator)
        self.music = self.eng.lib.load_sfx(music_fpath, True)
