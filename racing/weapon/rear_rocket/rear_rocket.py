from yyagl.gameobject import GameObject
from .gfx import RearRocketGfx
from .phys import RearRocketPhys
from .audio import RearRocketAudio
from .logic import RearRocketLogic
from .event import RearRocketEvent
from .ai import RearRocketAi


class RearRocketFacade(object):

    def attach_obs(self, meth):
        return self.logic.attach(meth)

    def detach_obs(self, meth):
        return self.logic.detach(meth)

    def fire(self):
        return self.logic.fire()

    def ai_fire(self):
        return self.ai.update()


class RearRocket(GameObject, RearRocketFacade):
    gfx_cls = RearRocketGfx
    phys_cls = RearRocketPhys
    audio_cls = RearRocketAudio
    logic_cls = RearRocketLogic
    event_cls = RearRocketEvent
    ai_cls = RearRocketAi

    def __init__(self, car, path, cars, particle_path):
        init_lst = [
            [('gfx', self.gfx_cls, [self, car.gfx.nodepath, path])],
            [('phys', self.phys_cls, [self, car, cars])],
            [('audio', self.audio_cls, [self])],
            [('logic', self.logic_cls, [self])],
            [('event', self.event_cls, [self, particle_path])],
            [('ai', self.ai_cls, [self, car])]]
        GameObject.__init__(self, init_lst)
