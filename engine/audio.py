from panda3d.core import AudioSound
from ..gameobject import Audio


class EngineAudio(Audio):

    @staticmethod
    def play(snd):
        if snd.status() != AudioSound.PLAYING:
            snd.play()
