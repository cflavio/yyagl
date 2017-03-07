from panda3d.core import TextNode
from direct.gui.OnscreenText import OnscreenText
from yyagl.gameobject import Gui
from .results import Results
from .loading.loading import Loading
from .minimap import Minimap


class RaceGui(Gui):

    def __init__(self, mdt, track, minimap_path, minimap_image, col_dct, font):
        Gui.__init__(self, mdt)
        self.results = Results()
        self.loading = Loading(mdt)
        self.debug_txt = OnscreenText(
            '', pos=(-.1, .1), scale=.05, fg=(1, 1, 1, 1),
            parent=eng.base.a2dBottomRight, align=TextNode.ARight)
        self.way_txt = OnscreenText(
            '', pos=(.1, .1), scale=.1, fg=(.75, .25, .25, 1),
            parent=eng.base.a2dBottomLeft, align=TextNode.ALeft,
            font=eng.font_mgr.load_font(font))
        self.track = track
        self.minimap_path = minimap_path
        self.minimap_image = minimap_image
        self.col_dct = col_dct

    def start(self):
        self.minimap = Minimap(
            self.track, game.track.phys.lrtb, self.minimap_path,
            self.minimap_image, self.col_dct)

    def destroy(self):
        Gui.destroy(self)
        self.results.destroy()
        self.loading.destroy()
        self.way_txt.destroy()
        self.minimap.destroy()
