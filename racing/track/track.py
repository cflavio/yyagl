from yyagl.gameobject import GameObjectMdt
from .gfx import TrackGfx
from .phys import TrackPhys
from .gui.gui import TrackGui
from .event import TrackEvent
import yaml


class Track(GameObjectMdt):

    def __init__(self, path, cb, split_world, submodels):
        eng.log_mgr.log('init track')
        self.path = path
        init_lst = [
            [('phys', TrackPhys, [self]),
             ('gfx', TrackGfx, [self, split_world, submodels],
              lambda: self.gfx.attach(self.on_loading)),
             ('gui', TrackGui, [self, path[6:]])],
            [('event', TrackEvent, [self])]]
        GameObjectMdt.__init__(self, init_lst, cb)
        with open('assets/models/%s/track.yml' % path) as track_file:
            self.camera_vector = yaml.load(track_file)['camera_vector']

    def on_loading(self, txt):
        self.notify('on_loading', txt)
