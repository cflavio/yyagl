from panda3d.core import AudioSound as PAudioSound


class PandaAudioSound(object):

    def __init__(self, fpath):
        self.snd = loader.loadSfx(fpath)

    def play(self):
        return self.snd.status() != PAudioSound.PLAYING and self.snd.play()

    def stop(self): return self.snd.stop()

    def set_loop(self, val): return self.snd.set_loop(val)

    def set_volume(self, val): return self.snd.set_volume(val)

    def set_play_rate(self, val): return self.snd.set_play_rate(val)

    def is_playing(self): return self.snd.status() == PAudioSound.PLAYING
