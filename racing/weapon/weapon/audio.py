from yyagl.gameobject import AudioColleague


class WeaponAudio(AudioColleague):

    sfx = 'assets/sfx/landing.ogg'

    def __init__(self, mediator):
        AudioColleague.__init__(self, mediator)
        self.sfx = loader.loadSfx(self.sfx)
