from panda3d.core import TextNode
from direct.gui.OnscreenText import OnscreenText
from .page import Page, PageGui, PageFacade
from .imgbtn import ImgBtn


class MainPageGui(PageGui):

    def bld_page(self):
        self.__bld_social()
        self.__bld_version()
        self._set_buttons()
        self.transition_enter()

    def __bld_social(self):
        sites = [
            ('facebook', 'http://www.facebook.com/Ya2Tech'),
            ('twitter', 'http://twitter.com/ya2tech'),
            ('google_plus', 'https://plus.google.com/118211180567488443153'),
            ('youtube',
             'http://www.youtube.com/user/ya2games?sub_confirmation=1'),
            ('pinterest', 'http://www.pinterest.com/ya2tech'),
            ('tumblr', 'http://ya2tech.tumblr.com'),
            ('feed', 'http://www.ya2.it/feed-following')]
        menu_args = self.props.menu_args
        self.widgets += [
            ImgBtn(
                parent=eng.base.a2dBottomRight,
                scale=.06,
                pos=(-1.0 + i*.15, 1, .1),
                frameColor=(1, 1, 1, 1),
                frameTexture=menu_args.social_imgs_dpath % site[0],
                command=eng.open_browser,
                extraArgs=[site[1]],
                **menu_args.imgbtn_args)
            for i, site in enumerate(sites)]

    def __bld_version(self):
        self.widgets += [OnscreenText(
            text=_('version: ') + eng.version,
            parent=eng.base.a2dBottomLeft, pos=(.02, .02), scale=.04,
            fg=(.8, .8, .8, 1), align=TextNode.ALeft,
            font=self.props.menu_args.font)]


class MainPage(Page, PageFacade):
    gui_cls = MainPageGui

    def __init__(self):
        PageFacade.__init__(self)
