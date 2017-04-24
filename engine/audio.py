from panda3d.core import AudioSound
from ..gameobject import Audio


class EngineAudio(Audio):

    def __init__(self, mdt, vol):
        Audio.__init__(self, mdt)
        self.set_volume(vol)

    @staticmethod
    def play(snd):
        if snd.status() != AudioSound.PLAYING:
            snd.play()

    def set_volume(self, vol):
        base.sfxManagerList[0].set_volume(vol)
