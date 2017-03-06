from yyagl.gameobject import Event
from panda3d.core import LPoint3f


class TrackEvent(Event):

    def __init__(self, mdt):
        Event.__init__(self, mdt)

    def start(self):
        eng.event.attach(self.on_frame)

    def on_frame(self):
        #cam_pos = game.player_car.logic.camera.camera.get_pos()
        nodepath = game.player_car.gfx.nodepath
        car_pos = nodepath.get_pos()
        if not game.options['development']['shaders']:
            sh_src = LPoint3f(*self.mdt.shadow_source)
            self.mdt.gfx.spot_lgt.setPos(car_pos + sh_src)
            #self.mdt.gfx.spot_lgt.lookAt(car_pos + (-40, 60, -50))
        cars = [game.player_car] + game.cars
        positions = [(car.name, car.gfx.nodepath.get_pos())
                     for car in cars]
        self.mdt.gui.minimap.update(positions)

    def destroy(self):
        Event.destroy(self)
        eng.event.detach(self.on_frame)
