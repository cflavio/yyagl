from yyagl.gameobject import Audio


class MineAudio(Audio):

    def __init__(self, mdt):
        Audio.__init__(self, mdt)
        self.sfx = loader.loadSfx('assets/sfx/landing.ogg')
