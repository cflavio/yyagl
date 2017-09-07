from panda3d.core import TextNode, Shader, TextureStage
from direct.gui.OnscreenText import OnscreenText
from direct.gui.DirectButton import DirectButton
from direct.gui.OnscreenImage import OnscreenImage
from yyagl.gameobject import Gui
from yyagl.engine.gui.page import Page, PageGui, PageEvent, PageFacade
from yyagl.gameobject import GameObject
from yyagl.engine.gui.menu import Menu


class RankingPageGui(PageGui):

    def __init__(self, mdt, menu, rprops, sprops):
        self.rprops = rprops
        self.sprops = sprops
        self.drivers = sprops.gameprops.drivers
        PageGui.__init__(self, mdt, menu)

    def bld_page(self):
        self.eng.init_gfx()
        self.font = self.mdt.menu.gui.menu_args.font
        self.text_fg = self.mdt.menu.gui.menu_args.text_fg
        self.text_bg = self.mdt.menu.gui.menu_args.text_bg
        self.text_err = self.mdt.menu.gui.menu_args.text_err
        items = game.logic.season.ranking.carname2points.items()
        sorted_ranking = reversed(sorted(items, key=lambda el: el[1]))
        txt = OnscreenText(text=_('Ranking'), scale=.1, pos=(0, .76),
                           font=self.font, fg=self.text_bg)
        self.add_widget(txt)
        for i, car in enumerate(sorted_ranking):
            txt, img = RankingGui.set_drv_txt_img(self, i, car[0], 0, .52,
                                                  str(car[1]) + ' %s')
            map(self.add_widget, [txt, img])
        track = self.rprops.track_name
        ntracks = len(self.sprops.gameprops.season_tracks)
        if self.sprops.gameprops.season_tracks.index(track) == ntracks - 1:
            cont_btn_cmd = game.logic.season.logic.next_race
            cont_btn_ea = []
        else:
            cont_btn_cmd = self.notify
            cont_btn_ea = ['on_ranking_end']
        cont_btn = DirectButton(
            text=_('Continue'), pos=(0, 1, -.8), command=cont_btn_cmd,
            extraArgs=cont_btn_ea, **self.rprops.season_props.gameprops.menu_args.btn_args)
        self.add_widget(cont_btn)
        PageGui.bld_page(self, False)


class RankingPage(Page):

    def __init__(self, rprops, sprops, menu):
        self.rprops = rprops
        self.menu = menu
        init_lst = [
            [('event', PageEvent, [self]),
             ('gui', RankingPageGui, [self, menu, rprops, sprops])]]
        GameObject.__init__(self, init_lst)
        PageFacade.__init__(self)

    def attach_obs(self, mth):
        self.gui.attach_obs(mth)

    def detach_obs(self, mth):
        self.gui.detach_obs(mth)


class RankingMenuGui(Gui):

    def __init__(self, mdt, rprops, sprops, menu):
        Gui.__init__(self, mdt)
        menu_args = sprops.gameprops.menu_args
        menu_args.btn_size = (-8.6, 8.6, -.42, .98)
        self.menu = Menu(menu_args)
        self.rank_page = RankingPage(rprops, sprops, self.menu)
        self.eng.do_later(.01, self.menu.push_page, [self.rank_page])

    def destroy(self):
        self.menu = self.menu.destroy()
        Gui.destroy(self)


class RankingMenu(GameObject):
    gui_cls = RankingMenuGui

    def __init__(self, rprops, sprops):
        init_lst = [[('gui', self.gui_cls, [self, rprops, sprops, self])]]
        GameObject.__init__(self, init_lst)

    def attach_obs(self, mth):
        self.gui.rank_page.attach_obs(mth)

    def detach_obs(self, mth):
        self.gui.rank_page.detach_obs(mth)


class RankingGui(Gui):

    def __init__(self, mdt, background_fpath, font, fg_col):
        Gui.__init__(self, mdt)
        self.ranking_texts = []
        self.background_path = background_fpath
        self.font = font
        self.fg_col = fg_col
        self.background = None

    @staticmethod
    def set_drv_txt_img(page, i, car_name, pos_x, top, text):
        idx, drvname, _, _ = next(
            driver for driver in page.drivers if driver[3] == car_name)
        is_player_car = car_name == page.rprops.season_props.player_car_name
        txt = OnscreenText(
            text=text % drvname, align=TextNode.A_left, scale=.072,
            pos=(pos_x, top - i * .16), font=page.font,
            fg=page.text_fg if is_player_car else page.text_bg)
        img = OnscreenImage(
            page.rprops.season_props.gameprops.cars_img % car_name,
            pos=(pos_x - .16, 1, top + .02 - i * .16), scale=.074)
        filtervpath = RankingGui.eng.curr_path + 'yyagl/assets/shaders/filter.vert'
        with open(filtervpath) as fvs:
            vert = fvs.read()
        drvfpath = RankingGui.eng.curr_path + 'yyagl/assets/shaders/drv_car.frag'
        with open(drvfpath) as ffs:
            frag = ffs.read()
        shader = Shader.make(Shader.SL_GLSL, vert, frag)
        img.set_shader(shader)
        img.set_transparency(True)
        t_s = TextureStage('ts')
        t_s.set_mode(TextureStage.MDecal)
        txt_path = page.rprops.season_props.gameprops.drivers_img.path_sel % idx
        img.set_texture(t_s, loader.loadTexture(txt_path))
        return txt, img

    def show(self, rprops, sprops):
        self.rank_menu = RankingMenu(rprops, sprops)

    def hide(self):
        self.rank_menu.destroy()

    def attach_obs(self, mth):
        self.rank_menu.attach_obs(mth)

    def detach_obs(self, mth):
        self.rank_menu.detach_obs(mth)

    def destroy(self):
        self.hide()
        self.ranking_texts = self.background = None
        Gui.destroy(self)
