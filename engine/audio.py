from ..gameobject import AudioColleague
from yyagl.lib.p3d.audio import P3dSound


AudioSound = P3dSound


class EngineAudio(AudioColleague):

    def __init__(self, mediator, vol=1.0):
        AudioColleague.__init__(self, mediator)
        self.set_volume(vol)

    def set_volume(self, vol): self.eng.lib.set_volume(vol)
