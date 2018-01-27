from ..gameobject import AudioColleague
from yyagl.library.panda.audio import PandaAudioSound


AudioSound = PandaAudioSound


class EngineAudio(AudioColleague):

    def __init__(self, mdt, vol=1.0):
        AudioColleague.__init__(self, mdt)
        self.set_volume(vol)

    def set_volume(self, vol): self.eng.lib.set_volume(vol)
