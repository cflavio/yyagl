from yyagl.gameobject import Audio


class WeaponAudio(Audio):

    sfx = 'assets/sfx/landing.ogg'

    def __init__(self, mdt):
        Audio.__init__(self, mdt)
        self.sfx = loader.loadSfx(self.sfx)
