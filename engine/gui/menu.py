from direct.gui.DirectGuiGlobals import FLAT
from direct.gui.OnscreenImage import OnscreenImage
from ...gameobject import Gui, Logic, GameObject
from ..font import FontMgr


class MenuArgs(object):

    def __init__(self, font, text_fg, text_bg, text_err, text_scale, btn_size,
                 btn_color, background_img, rollover_sfx, click_sfx,
                 social_imgs_dpath):
        self.font = FontMgr().load_font(font)
        self.text_fg = text_fg
        self.text_bg = text_bg
        self.text_err = text_err
        self.text_scale = text_scale
        self.btn_size = btn_size
        self.btn_color = btn_color
        self.background_img = background_img
        self.rollover_sfx = loader.loadSfx(rollover_sfx)
        self.click_sfx = loader.loadSfx(click_sfx)
        self.social_imgs_dpath = social_imgs_dpath

    @property
    def btn_args(self):  # it may be used without a menu e.g. results
        return {
            'scale': self.text_scale,
            'text_font': self.font,
            'text_fg': self.text_fg,
            'frameColor': self.btn_color,
            'frameSize': self.btn_size,
            'rolloverSound': self.rollover_sfx,
            'clickSound': self.click_sfx}

    @property
    def imgbtn_args(self):
        return {
            'rolloverSound': self.rollover_sfx,
            'clickSound': self.click_sfx}

    @property
    def label_args(self):
        return {
            'scale': self.text_scale,
            'text_fg': self.text_fg,
            'text_font': self.font,
            'frameColor': (1, 1, 1, 0)}

    @property
    def option_args(self):
        tfg = self.text_fg
        return {
            'scale': self.text_scale,
            'text_font': self.font,
            'text_fg': tfg,
            'frameColor': self.btn_color,
            'frameSize': self.btn_size,
            'rolloverSound': self.rollover_sfx,
            'clickSound': self.click_sfx,
            'text_scale': .85,
            'item_text_font': self.font,
            'item_frameColor': tfg,
            'item_relief': FLAT,
            'popupMarker_frameColor': self.btn_color,
            'textMayChange': 1,
            'highlightColor': (tfg[0] * 1.2, tfg[1] * 1.2, tfg[2] * 1.2, .2)}

    @property
    def checkbtn_args(self):
        return {
            'scale': self.text_scale,
            'text_font': self.font,
            'text_fg': self.text_fg,
            'frameColor': self.btn_color,
            'rolloverSound': self.rollover_sfx,
            'clickSound': self.click_sfx}

    @property
    def text_args(self):
        return {
            'scale': self.text_scale,
            'fg': self.text_fg,
            'font': self.font}


class MenuGui(Gui):

    def __init__(self, mdt, menu_args):
        Gui.__init__(self, mdt)
        self.menu_args = menu_args
        self.background_img = None
        if self.menu_args.background_img:
            self.background = OnscreenImage(scale=(1.77778, 1, 1.0),
                                            image=self.menu_args.background_img)
            self.background.setBin('background', 10)

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
            self.pages[-1].hide()
            if len(self.pages) > 1:
                self.pages[-1].detach_obs(self.on_back)
        self.pages += [page]
        page.attach_obs(self.on_back)
        page.attach_obs(self.on_push_page)

    def on_push_page(self, page):
        self.push_page(page)

    def on_back(self):
        page = self.pages.pop()
        page.detach_obs(self.on_back)
        page.destroy()
        self.pages[-1].show()
        self.pages[-1].attach_obs(self.on_back)

    def destroy(self):
        Logic.destroy(self)
        map(lambda page: page.destroy(), self.pages)
        self.pages = None


class MenuFacade(object):

    def push_page(self, page):
        return self.logic.push_page(page)

    def attach_obs(self, meth):
        return self.gui.attach(meth)

    def detach_obs(self, meth):
        return self.gui.detach(meth)


class Menu(GameObject, MenuFacade):
    gui_cls = MenuGui

    def __init__(self, menu_args):
        comps = [
            [('gui', self.gui_cls, [self, menu_args])],
            [('logic', MenuLogic, [self])]]
        GameObject.__init__(self, comps)
