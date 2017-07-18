from yyagl.gameobject import GameObject
from .gfx import RocketGfx
from .phys import RocketPhys
from .audio import RocketAudio
from .logic import RocketLogic
from .event import RocketEvent
from .ai import RocketAi


class RocketFacade(object):

    def attach_obs(self, meth):
        return self.logic.attach(meth)

    def detach_obs(self, meth):
        return self.logic.detach(meth)

    def fire(self):
        return self.logic.fire()

    def ai_fire(self):
        return self.ai.update()


class Rocket(GameObject, RocketFacade):

    def __init__(self, car, path, cars, particle_path):
        init_lst = [
            [('gfx', RocketGfx, [self, car.gfx.nodepath, path])],
            [('phys', RocketPhys, [self, car, cars])],
            [('audio', RocketAudio, [self])],
            [('logic', RocketLogic, [self])],
            [('event', RocketEvent, [self, particle_path])],
            [('ai', RocketAi, [self, car])]]
        GameObject.__init__(self, init_lst)
