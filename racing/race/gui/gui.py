from panda3d.core import TextNode
from direct.gui.OnscreenText import OnscreenText
from yyagl.gameobject import Gui
from .results import Results, ResultProps
from .loading.loading import Loading
from .minimap import Minimap


class RaceGuiProps(object):

    def __init__(
        self, minimap_path, minimap_image, col_dct, font, cars, menu_args,
        drivers_img, cars_imgs, share_urls, share_imgs, track_name, car_name):
        self.minimap_path = minimap_path
        self.minimap_image = minimap_image
        self.col_dct = col_dct
        self.font = font
        self.cars = cars
        self.menu_args = menu_args
        self.drivers_img = drivers_img
        self.cars_imgs = cars_imgs
        self.share_urls = share_urls
        self.share_imgs = share_imgs
        self.track_name = track_name
        self.car_name = car_name


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
        self.loading = Loading(mdt)
        self.debug_txt = OnscreenText(
            '', pos=(-.1, .1), scale=.05, fg=(1, 1, 1, 1),
            parent=eng.base.a2dBottomRight, align=TextNode.ARight)
        self.way_txt = OnscreenText(
            '', pos=(.1, .1), scale=.1, fg=r_p.menu_args.text_err,
            parent=eng.base.a2dBottomLeft, align=TextNode.ALeft,
            font=eng.font_mgr.load_font(r_p.font))

    def start(self):
        self.minimap = Minimap(
            self.mdt.track.lrtb, self.props.minimap_path,
            self.props.minimap_image, self.props.col_dct, self.props.cars,
            self.props.car_name)

    def destroy(self):
        self.results.destroy()
        self.loading.destroy()
        self.way_txt.destroy()
        self.minimap.destroy()
        Gui.destroy(self)
