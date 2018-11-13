from yyagl.lib.gui import Text
from .page import Page, PageGui, PageFacade
from .imgbtn import ImgBtn


class MainPageGui(PageGui):

    def build(self, back_btn=True, exit_behav=False):
        self.__build_social()
        self.__build_version()
        self._set_widgets()
        self.transition_enter()

    def __build_social(self):
        sites = self.props.gameprops.social_sites
        menu_props = self.props.gameprops.menu_props
        left = (len(sites) - 1) / 2.0 * .15
        buttons = [
            ImgBtn(
                parent='bottomcenter',
                scale=(.06, .06),
                pos=(-left + i*.15, .1),
                frame_col=(1, 1, 1, 1),
                frame_texture=menu_props.social_imgs_dirpath % site[0],
                cmd=self.eng.open_browser,
                extra_args=[site[1]],
                **menu_props.imgbtn_args)
            for i, site in enumerate(sites)]
        self.add_widgets(buttons)

    def __build_version(self):
        txt = Text(
            _('version: ') + self.eng.version, parent='bottomleft',
            pos=(.02, .02), scale=.04, fg=(.8, .8, .8, 1), align='left',
            font=self.props.gameprops.menu_props.font)
        self.add_widgets([txt])


class MainPage(Page, PageFacade):
    gui_cls = MainPageGui

    def __init__(self):
        # refactor: call Page.__init__
        PageFacade.__init__(self)
