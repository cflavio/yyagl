from panda3d.core import AudioSound
from yyagl.facade import Facade


class P3dSound(Facade):

    def __init__(self, filepath):
        self.snd = loader.loadSfx(filepath)
        self._fwd_mth('stop', lambda obj: obj.snd.stop)
        self._fwd_mth('set_loop', lambda obj: obj.snd.set_loop)
        self._fwd_mth('set_volume', lambda obj: obj.snd.set_volume)
        self._fwd_mth('set_play_rate', lambda obj: obj.snd.set_play_rate)

    def play(self):
        if self.snd.status() != AudioSound.PLAYING: return self.snd.play()

    @property
    def playing(self): return self.snd.status() == AudioSound.PLAYING
