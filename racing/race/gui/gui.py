from panda3d.core import TextNode
from direct.gui.OnscreenText import OnscreenText
from yyagl.gameobject import Gui
from yyagl.engine.font import FontMgr
from .results import Results, ResultProps
from .loading.loading import Loading
from .minimap import Minimap


class RaceGuiFacade(object):

    def update_minimap(self, positions):
        return self.minimap.update(positions)


class RaceGui(Gui, RaceGuiFacade):

    def __init__(self, mdt, racegui_props):
        Gui.__init__(self, mdt)
        r_p = self.props = racegui_props
        result_props = ResultProps(
            r_p.menu_args, r_p.drivers_img, r_p.cars_imgs, r_p.share_urls,
            r_p.share_imgs, r_p.track_name)
        self.results = Results(result_props)
        self.loading = Loading()
        self.debug_txt = OnscreenText(
            '', pos=(-.1, .1), scale=.05, fg=(1, 1, 1, 1),
            parent=eng.base.a2dBottomRight, align=TextNode.ARight)
        self.way_txt = OnscreenText(
            '', pos=(.1, .1), scale=.1, fg=r_p.menu_args.text_err,
            parent=eng.base.a2dBottomLeft, align=TextNode.ALeft,
            font=FontMgr().load_font(r_p.font))
        self.minimap = None

    def start(self):
        self.minimap = Minimap(
            self.mdt.track.lrtb, self.props.minimap_path,
            self.props.minimap_image, self.props.col_dct, self.props.cars,
            self.props.player_car_name)

    def destroy(self):
        self.results.destroy()
        # self.loading.destroy()
        self.way_txt.destroy()
        self.minimap.destroy()
        Gui.destroy(self)
