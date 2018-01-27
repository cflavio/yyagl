from panda3d.core import LPoint3f
from yyagl.gameobject import EventColleague


class TrackEvent(EventColleague):

    def __init__(self, mediator, shaders, shadow_src):
        EventColleague.__init__(self, mediator)
        self.shaders = shaders
        self.shadow_src = shadow_src

    def update(self, car_pos):
        if not self.shaders:
            sh_src = LPoint3f(*self.shadow_src)
            self.mediator.gfx.spot_lgt.setPos(car_pos + sh_src)
