from panda3d.core import AudioSound
from yyagl.facade import Facade


class P3dSound(Facade):

    def __init__(self, filepath):
        self.snd = loader.loadSfx(filepath)
        mth_lst = [
            ('stop', lambda obj: obj.snd.stop),
            ('set_loop', lambda obj: obj.snd.set_loop),
            ('set_volume', lambda obj: obj.snd.set_volume),
            ('set_play_rate', lambda obj: obj.snd.set_play_rate)]
        Facade.__init__(self, mth_lst=mth_lst)

    def play(self):
        if self.snd.status() != AudioSound.PLAYING: return self.snd.play()

    @property
    def playing(self): return self.snd.status() == AudioSound.PLAYING
