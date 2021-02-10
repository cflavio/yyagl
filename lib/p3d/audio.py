from panda3d.core import AudioSound


class P3dSound:

    def __init__(self, filepath):
        self.snd = loader.loadSfx(filepath)

    def stop(self): return self.snd.stop()
    def set_loop(self, val): return self.snd.set_loop(val)
    def set_volume(self, vol): return self.snd.set_volume(vol)
    def set_play_rate(self, rate): return self.snd.set_play_rate(rate)

    def play(self):
        if self.snd.status() != AudioSound.PLAYING: return self.snd.play()
        return None

    @property
    def playing(self): return self.snd.status() == AudioSound.PLAYING
