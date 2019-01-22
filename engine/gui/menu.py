from direct.gui.DirectGuiGlobals import FLAT
from yyagl.gameobject import GuiColleague, LogicColleague, GameObject
from yyagl.facade import Facade
from yyagl.lib.gui import Img
from yyagl.engine.audio import AudioSound


class NavInfoPerPlayer:

    def __init__(self, left, right, up, down, fire):
        self.left = left
        self.right = right
        self.up = up
        self.down = down
        self.fire = fire


class NavInfo:

    def __init__(self, navinfo_lst):
        self.navinfo_lst = navinfo_lst


class MenuProps(GameObject):

    def __init__(
            self, font_path, text_active_col, text_normal_col, text_err_col,
            text_scale, btn_size, btn_col, background_img_path, over_sfx_path,
            click_sfx_path, social_imgs_dirpath, nav):
        GameObject.__init__(self)
        self.__font_path = font_path
        self.text_active_col = text_active_col
        self.text_normal_col = text_normal_col
        self.text_err_col = text_err_col
        self.text_scale = text_scale
        self.btn_size = btn_size
        self.btn_col = btn_col
        self.background_img_path = background_img_path
        self.__over_sfx_path = over_sfx_path
        self.__click_sfx_path = click_sfx_path
        self.social_imgs_dirpath = social_imgs_dirpath
        self.nav = nav

    @property
    def font(self): return self.eng.font_mgr.load_font(self.__font_path)

    @property
    def over_sfx(self): return AudioSound(self.__over_sfx_path).snd

    @property
    def click_sfx(self): return AudioSound(self.__click_sfx_path).snd

    @property
    def btn_args(self):  # it may be used without a menu e.g. results
        return {
            'scale': (self.text_scale, self.text_scale),
            'text_font': self.font,
            'text_fg': self.text_active_col,
            'frame_col': self.btn_col,
            'frame_size': self.btn_size,
            'over_snd': self.over_sfx,
            'click_snd': self.click_sfx}

    @property
    def imgbtn_args(self):
        return {
            'over_snd': self.over_sfx,
            'click_snd': self.click_sfx}

    @property
    def label_args(self):
        return {
            'scale': self.text_scale,
            'text_fg': self.text_normal_col,
            'text_font': self.font,
            'frame_col': (1, 1, 1, 0)}

    @property
    def option_args(self):
        tfg = self.text_active_col
        return {
            'scale': self.text_scale,
            'text_font': self.font,
            'text_fg': tfg,
            'frame_col': self.btn_col,
            'frame_size': self.btn_size,
            'over_snd': self.over_sfx,
            'click_snd': self.click_sfx,
            'text_scale': .85,
            'item_text_font': self.font,
            'item_frame_col': tfg,
            'item_relief': FLAT,
            'popup_marker_col': self.btn_col,
            'text_may_change': 1,
            'highlight_col': (tfg[0] * 1.2, tfg[1] * 1.2, tfg[2] * 1.2, .2)}

    @property
    def checkbtn_args(self):
        return {
            'scale': self.text_scale,
            'text_font': self.font,
            'text_fg': self.text_active_col,
            'frame_col': self.btn_col,
            'over_snd': self.over_sfx,
            'click_snd': self.click_sfx}

    @property
    def text_args(self):
        return {
            'scale': self.text_scale,
            'fg': self.text_normal_col,
            'font': self.font}


class MenuGui(GuiColleague):

    def __init__(self, mediator, menu_props):
        GuiColleague.__init__(self, mediator)
        self.menu_props = menu_props
        self.background = None
        if not self.menu_props.background_img_path: return
        self.background = Img(self.menu_props.background_img_path,
                              scale=(1.77778, 1, 1.0),
                              background=True)

    def destroy(self):
        if self.background: self.background.destroy()
        self.menu_props = self.background = None
        GuiColleague.destroy(self)


class MenuLogic(LogicColleague):

    def __init__(self, mediator):
        LogicColleague.__init__(self, mediator)
        self.pages = []

    def push_page(self, page):
        if self.pages:
            self.pages[-1].hide()
            if len(self.pages) > 1:  # first page doesn't go back
                self.pages[-1].detach_obs(self.on_back)
                self.pages[-1].detach_obs(self.on_quit)
        self.pages += [page]
        list(map(page.attach_obs, [self.on_back, self.on_quit, self.on_push_page]))

    def enable(self): self.pages[-1].enable()

    def enable_navigation(self): self.pages[-1].enable_navigation()

    def disable(self): self.pages[-1].disable()

    def disable_navigation(self): self.pages[-1].disable_navigation()

    def on_push_page(self, page_code, args=[]): pass

    def __back_quit_tmpl(self, idx, fun):
        page = self.pages.pop()
        list(map(page.detach_obs, [self.on_back, self.on_quit]))
        page.destroy()
        fun()
        self.pages[idx].show()
        list(map(self.pages[idx].attach_obs, [self.on_back, self.on_quit]))

    def on_back(self):
        self.__back_quit_tmpl(-1, lambda: None)

    def on_quit(self):
        def __on_quit():
            while len(self.pages) > 1:
                page = self.pages.pop()
                page.destroy()
        self.__back_quit_tmpl(0, __on_quit)

    def destroy(self):
        list(map(lambda page: page.destroy(), self.pages))
        self.pages = None
        LogicColleague.destroy(self)


class MenuFacade(Facade):

    def __init__(self):
        mth_lst = [
            ('push_page', lambda obj: obj.logic.push_page),
            ('attach_obs', lambda obj: obj.gui.attach),
            ('detach_obs', lambda obj: obj.gui.detach),
            ('enable', lambda obj: obj.logic.enable),
            ('enable_navigation', lambda obj: obj.logic.enable_navigation)]
        Facade.__init__(self, mth_lst=mth_lst)


class Menu(GameObject, MenuFacade):
    gui_cls = MenuGui
    logic_cls = MenuLogic

    def __init__(self, menu_props):
        comps = [
            [('logic', self.logic_cls, [self])],
            [('gui', self.gui_cls, [self, menu_props])]]
        GameObject.__init__(self, comps)
        MenuFacade.__init__(self)

    def destroy(self):
        GameObject.destroy(self)
        MenuFacade.destroy(self)
