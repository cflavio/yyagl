from direct.gui.DirectGuiGlobals import FLAT
from ...gameobject import GuiColleague, LogicColleague, GameObject
from ...facade import Facade
from ...library.gui import Img


class MenuArgs(GameObject):

    def __init__(self, font, text_active, text_normal, text_err, text_scale,
                 btn_size, btn_color, background_img, rollover_sfx, click_sfx,
                 social_imgs_dpath):
        GameObject.__init__(self)
        self.__font = font
        self.text_active = text_active
        self.text_normal = text_normal
        self.text_err = text_err
        self.text_scale = text_scale
        self.btn_size = btn_size
        self.btn_color = btn_color
        self.background_img = background_img
        self.__rollover_sfx = rollover_sfx
        self.__click_sfx = click_sfx
        self.social_imgs_dpath = social_imgs_dpath

    @property
    def font(self):
        return self.eng.font_mgr.load_font(self.__font)

    @property
    def rollover_sfx(self):
        return loader.loadSfx(self.__rollover_sfx)

    @property
    def click_sfx(self):
        return loader.loadSfx(self.__click_sfx)

    @property
    def btn_args(self):  # it may be used without a menu e.g. results
        return {
            'scale': self.text_scale,
            'text_font': self.font,
            'text_fg': self.text_active,
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
            'text_fg': self.text_normal,
            'text_font': self.font,
            'frameColor': (1, 1, 1, 0)}

    @property
    def option_args(self):
        tfg = self.text_active
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
            'text_fg': self.text_active,
            'frameColor': self.btn_color,
            'rolloverSound': self.rollover_sfx,
            'clickSound': self.click_sfx}

    @property
    def text_args(self):
        return {
            'scale': self.text_scale,
            'fg': self.text_normal,
            'font': self.font}


class MenuGui(GuiColleague):

    def __init__(self, mediator, menu_args):
        GuiColleague.__init__(self, mediator)
        self.menu_args = menu_args
        self.background = None
        if not self.menu_args.background_img: return
        self.background = Img(self.menu_args.background_img,
                              scale=(1.77778, 1, 1.0),
                              is_background=True)

    def destroy(self):
        GuiColleague.destroy(self)
        if self.background: self.background.destroy()


class MenuLogic(LogicColleague):

    def __init__(self, mediator):
        LogicColleague.__init__(self, mediator)
        self.pages = []

    def push_page(self, page):
        if self.pages:
            self.pages[-1].hide()
            if len(self.pages) > 1:
                self.pages[-1].detach_obs(self.on_back)
                self.pages[-1].detach_obs(self.on_quit)
        self.pages += [page]
        map(page.attach_obs, [self.on_back, self.on_quit, self.on_push_page])

    def enable(self, val):
        (self.pages[-1].enable if val else self.pages[-1].disable)()

    def enable_navigation(self, val):
        page = self.pages[-1]
        (page.enable_navigation if val else page.disable_navigation)()

    def on_push_page(self, page_code, args=[]):
        pass

    def on_back(self):
        page = self.pages.pop()
        page.detach_obs(self.on_back)
        page.detach_obs(self.on_quit)
        page.destroy()
        self.pages[-1].show()
        self.pages[-1].attach_obs(self.on_back)
        self.pages[-1].attach_obs(self.on_quit)

    def on_quit(self):
        page = self.pages.pop()
        page.detach_obs(self.on_back)
        page.detach_obs(self.on_quit)
        page.destroy()
        while len(self.pages) > 1:
            page = self.pages.pop()
            page.destroy()
        self.pages[0].show()
        self.pages[0].attach_obs(self.on_back)
        self.pages[0].attach_obs(self.on_quit)

    def destroy(self):
        map(lambda page: page.destroy(), self.pages)
        self.pages = None
        LogicColleague.destroy(self)


class MenuFacade(Facade):

    def __init__(self):
        fwd_mths = [
            ('push_page', lambda obj: obj.logic.push_page),
            ('attach_obs', lambda obj: obj.gui.attach),
            ('detach_obs', lambda obj: obj.gui.detach),
            ('enable', lambda obj: obj.logic.enable),
            ('enable_navigation', lambda obj: obj.logic.enable_navigation)]
        map(lambda args: self._fwd_mth(*args), fwd_mths)


class Menu(GameObject, MenuFacade):
    gui_cls = MenuGui
    logic_cls = MenuLogic

    def __init__(self, menu_args):
        comps = [
            [('logic', self.logic_cls, [self])],
            [('gui', self.gui_cls, [self, menu_args])]]
        GameObject.__init__(self, comps)
        MenuFacade.__init__(self)

    def destroy(self):
        GameObject.destroy(self)
        MenuFacade.destroy(self)
