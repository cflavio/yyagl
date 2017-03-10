from direct.gui.DirectGuiGlobals import FLAT
from direct.gui.OnscreenImage import OnscreenImage
from ...gameobject import Gui, Logic, GameObjectMdt


class MenuArgs(object):

    def __init__(self, font, text_fg, text_bg, text_scale, btn_size,
                 btn_color, background, rollover, click, social_path):
        self.font = eng.font_mgr.load_font(font)
        self.text_fg = text_fg
        self.text_bg = text_bg
        self.text_scale = text_scale
        self.btn_size = btn_size
        self.btn_color = btn_color
        self.background = background
        self.rollover = loader.loadSfx(rollover)
        self.click = loader.loadSfx(click)
        self.social_path = social_path


class MenuGui(Gui):

    def __init__(self, mdt, menu_args):
        Gui.__init__(self, mdt)
        self.menu_args = menu_args
        self.background = None
        if self.menu_args.background:
            self.background = OnscreenImage(scale=(1.77778, 1, 1.0),
                                            image=self.menu_args.background)
            self.background.setBin('background', 10)

    @property
    def imgbtn_args(self):
        return {
            'rolloverSound': self.menu_args.rollover,
            'clickSound': self.menu_args.click}

    @property
    def btn_args(self):
        return {
            'scale': self.menu_args.text_scale,
            'text_font': self.menu_args.font,
            'text_fg': self.menu_args.text_fg,
            'frameColor': self.menu_args.btn_color,
            'frameSize': self.menu_args.btn_size,
            'rolloverSound': self.menu_args.rollover,
            'clickSound': self.menu_args.click}

    @property
    def label_args(self):
        return {
            'scale': self.menu_args.text_scale,
            'text_fg': self.menu_args.text_fg,
            'text_font': self.menu_args.font,
            'frameColor': (1, 1, 1, 0)}

    @property
    def option_args(self):
        tfg = self.menu_args.text_fg
        return {
            'scale': self.menu_args.text_scale,
            'text_font': self.menu_args.font,
            'text_fg': tfg,
            'frameColor': self.menu_args.btn_color,
            'frameSize': self.menu_args.btn_size,
            'rolloverSound': self.menu_args.rollover,
            'clickSound': self.menu_args.click,
            'text_scale': .85,
            'item_text_font': self.menu_args.font,
            'item_frameColor': tfg,
            'item_relief': FLAT,
            'popupMarker_frameColor': self.menu_args.btn_color,
            'textMayChange': 1,
            'highlightColor': (tfg[0] * 1.2, tfg[1] * 1.2, tfg[2] * 1.2, .2)}

    @property
    def checkbtn_args(self):
        return {
            'scale': self.menu_args.text_scale,
            'text_font': self.menu_args.font,
            'text_fg': self.menu_args.text_fg,
            'frameColor': self.menu_args.btn_color,
            'rolloverSound': self.menu_args.rollover,
            'clickSound': self.menu_args.click}

    @property
    def text_args(self):
        return {
            'scale': self.menu_args.text_scale,
            'fg': self.menu_args.text_fg,
            'font': self.menu_args.font}

    def destroy(self):
        Gui.destroy(self)
        if self.background:
            self.background.destroy()


class MenuLogic(Logic):

    def __init__(self, mdt):
        Logic.__init__(self, mdt)
        self.pages = []

    def push_page(self, page):
        if self.pages:
            self.pages[-1].gui.hide()
            if len(self.pages) > 1:
                self.pages[-1].gui.detach(self.on_back)
        self.pages += [page]
        page.gui.attach(self.on_back)

    def on_back(self):
        page = self.pages.pop()
        page.gui.detach(self.on_back)
        page.destroy()
        self.pages[-1].gui.show()
        self.pages[-1].gui.attach(self.on_back)

    def destroy(self):
        Logic.destroy(self)
        map(lambda page: page.destroy(), self.pages)
        self.pages = None


class Menu(GameObjectMdt):
    gui_cls = MenuGui

    def __init__(self, menu_args):
        init_lst = [
            [('gui', self.gui_cls, [self, menu_args])],
            [('logic', MenuLogic, [self])]]
        GameObjectMdt.__init__(self, init_lst)
