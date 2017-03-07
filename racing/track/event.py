from panda3d.core import LPoint3f
from yyagl.gameobject import Event


class TrackEvent(Event):

    def __init__(self, mdt, shaders):
        Event.__init__(self, mdt)
        self.shaders = shaders

    def start(self):
        eng.event.attach(self.on_frame)

    def update(self, car_pos):
        if not self.shaders:
            sh_src = LPoint3f(*self.mdt.shadow_source)
            self.mdt.gfx.spot_lgt.setPos(car_pos + sh_src)
            #self.mdt.gfx.spot_lgt.lookAt(car_pos + (-40, 60, -50))
