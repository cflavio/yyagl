from yyagl.gameobject import GameObjectMdt
from .gfx import RocketGfx
from .phys import RocketPhys
from .audio import RocketAudio
from .logic import RocketLogic


class Rocket(GameObjectMdt):
    gfx_cls = RocketGfx
    phys_cls = RocketPhys
    audio_cls = RocketAudio
    logic_cls = RocketLogic

    def __init__(self, car, path):
        init_lst = [
            [('gfx', self.gfx_cls, [self, car.gfx.nodepath, path])],
            [('phys', self.phys_cls, [self, car.gfx.nodepath])],
            [('audio', self.audio_cls, [self])],
            [('logic', self.logic_cls, [self])]]
        GameObjectMdt.__init__(self, init_lst)
