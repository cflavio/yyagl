from panda3d.core import TextNode
from direct.gui.OnscreenText import OnscreenText
from .page import Page, PageGui, PageFacade
from .imgbtn import ImgBtn


class MainPageGui(PageGui):

    def build(self, back_btn=True):
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
            ('feed', 'http://www.ya2.it/pages/feed-following.html')]
        menu_args = self.props.gameprops.menu_args
        left = (len(sites) - 1) / 2.0 * .15
        self.widgets += [
            ImgBtn(
                parent=base.a2dBottomCenter,
                scale=.06,
                pos=(-left + i*.15, 1, .1),
                frameColor=(1, 1, 1, 1),
                frameTexture=menu_args.social_imgs_dpath % site[0],
                command=self.eng.open_browser,
                extraArgs=[site[1]],
                **menu_args.imgbtn_args)
            for i, site in enumerate(sites)]

    def __bld_version(self):
        self.widgets += [OnscreenText(
            text=_('version: ') + self.eng.version,
            parent=base.a2dBottomLeft, pos=(.02, .02), scale=.04,
            fg=(.8, .8, .8, 1), align=TextNode.ALeft,
            font=self.props.gameprops.menu_args.font)]


class MainPage(Page, PageFacade):
    gui_cls = MainPageGui

    def __init__(self):
        # refactor: call Page.__init__
        PageFacade.__init__(self)
