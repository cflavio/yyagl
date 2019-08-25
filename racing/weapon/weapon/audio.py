from yyagl.gameobject import AudioColleague


class WeaponAudio(AudioColleague):

    sfx = 'assets/sfx/landing.ogg'
    crash_sfx = 'assets/sfx/crash_high_speed.ogg'

    def __init__(self, mediator):
        AudioColleague.__init__(self, mediator)
        self.sfx = loader.loadSfx(self.sfx)
        self.crash_sfx = loader.loadSfx(self.crash_sfx)
