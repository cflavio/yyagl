from yyagl.lib.gui import Text
from .page import Page, PageGui, PageFacade
from .imgbtn import ImgBtn


class MainPageGui(PageGui):

    def build(self, back_btn=True):  # the signature is different from the
        self.__build_social()        # inherited one
        self.__build_version()
        self._set_widgets()
        self.transition_enter()

    def __build_social(self):
        sites = self.props.gameprops.social_sites
        menu_args = self.props.gameprops.menu_args
        left = (len(sites) - 1) / 2.0 * .15
        buttons = [
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
        self.widgets += buttons

    def __build_version(self):
        txt = Text(
            _('version: ') + self.eng.version, parent='bottomleft',
            pos=(.02, .02), scale=.04, fg=(.8, .8, .8, 1), align='left',
            font=self.props.gameprops.menu_args.font)
        self.widgets += [txt]


class MainPage(Page, PageFacade):
    gui_cls = MainPageGui

    def __init__(self):
        # refactor: call Page.__init__
        PageFacade.__init__(self)
