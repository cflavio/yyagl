from yyagl.gameobject import AudioColleague


class WeaponAudio(AudioColleague):

    sfx = 'assets/sfx/landing.ogg'

    def __init__(self, mdt):
        AudioColleague.__init__(self, mdt)
        self.sfx = loader.loadSfx(self.sfx)
