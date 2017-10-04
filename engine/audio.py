from ..gameobject import Audio
from yyagl.library.panda.audio import PandaAudioSound


AudioSound = PandaAudioSound


class EngineAudio(Audio):

    def __init__(self, mdt, vol=1.0):
        Audio.__init__(self, mdt)
        self.set_volume(vol)

    def set_volume(self, vol): self.eng.lib.set_volume(vol)
