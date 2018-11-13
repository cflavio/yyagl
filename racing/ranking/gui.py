from panda3d.core import TextNode, Shader, TextureStage
from yyagl.lib.gui import Btn, Text, Img
from yyagl.lib.p3d.shader import load_shader
from yyagl.gameobject import GuiColleague
from yyagl.engine.gui.page import Page, PageGui, PageEvent, PageFacade
from yyagl.gameobject import GameObject
from yyagl.engine.gui.menu import Menu


class RankingPageGui(PageGui):

    def __init__(self, mediator, menu, rprops, sprops, ranking):
        self.rprops = rprops
        self.sprops = sprops
        self.drivers = sprops.drivers
        self.ranking = ranking
        PageGui.__init__(self, mediator, menu)

    def build(self, back_btn=True):
        self.eng.init_gfx()
        self.font = self.mediator.menu.gui.menu_props.font
        self.text_fg = self.mediator.menu.gui.menu_props.text_active_col
        self.text_bg = self.mediator.menu.gui.menu_props.text_normal_col
        self.text_err_col = self.mediator.menu.gui.menu_props.text_err_col
        items = self.ranking.carname2points.items()
        sorted_ranking = reversed(sorted(items, key=lambda el: el[1]))
        txt = Text(_('Ranking'), scale=.1, pos=(0, .76),
                           font=self.font, fg=self.text_bg)
        self.add_widgets([txt])
        for i, car in enumerate(sorted_ranking):
            txt, img = RankingGui.set_drv_txt_img(self, i, car[0], 0, .52,
                                                  str(car[1]) + ' %s')
            self.add_widgets([txt, img])
        track = self.rprops.track_name
        ntracks = len(self.sprops.gameprops.season_tracks)
        if self.sprops.gameprops.season_tracks.index(track) == ntracks - 1:
            cont_btn_cmd = self.notify
            cont_btn_ea = ['on_ranking_next_race']
            img = Img(
                'assets/images/gui/trophy.txo', parent=base.a2dRightCenter,
                pos=(-.58, 0), scale=.55)
            img.set_transparency(True)
            txt = Text(
                _('Congratulations!'), fg=(.8, .6, .2, 1), scale=.16,
                pos=(0, -.3), font=loader.loadFont(self.sprops.font),
                parent='leftcenter')
            txt.set_r(-79)
            self.add_widgets([txt, img])
        else:
            cont_btn_cmd = self.notify
            cont_btn_ea = ['on_ranking_end']
        cont_btn = Btn(
            text=_('Continue'), pos=(0, 1, -.8), command=cont_btn_cmd,
            extraArgs=cont_btn_ea,
            **self.rprops.season_props.gameprops.menu_props.btn_args)
        self.add_widgets([cont_btn])
        PageGui.build(self, False)


class RankingPage(Page):

    def __init__(self, rprops, sprops, menu, ranking):
        self.rprops = rprops
        self.menu = menu
        init_lst = [
            [('event', PageEvent, [self]),
             ('gui', RankingPageGui, [self, menu, rprops, sprops, ranking])]]
        GameObject.__init__(self, init_lst)
        PageFacade.__init__(self)
        # invece Page's __init__

    def attach_obs(self, mth):
        self.gui.attach_obs(mth)

    def detach_obs(self, mth):
        self.gui.detach_obs(mth)

    def destroy(self):
        GameObject.destroy(self)
        PageFacade.destroy(self)


class RankingMenuGui(GuiColleague):

    def __init__(self, mediator, rprops, sprops, ranking):
        GuiColleague.__init__(self, mediator)
        menu_props = sprops.gameprops.menu_props
        menu_props.btn_size = (-8.6, 8.6, -.42, .98)
        self.menu = Menu(menu_props)
        self.rank_page = RankingPage(rprops, sprops, self.menu, ranking)
        self.eng.do_later(.01, self.menu.push_page, [self.rank_page])

    def destroy(self):
        self.menu = self.menu.destroy()
        GuiColleague.destroy(self)


class RankingMenu(GameObject):
    gui_cls = RankingMenuGui

    def __init__(self, rprops, sprops, ranking):
        init_lst = [[('gui', self.gui_cls, [self, rprops, sprops, ranking])]]
        GameObject.__init__(self, init_lst)

    def attach_obs(self, mth):
        self.gui.rank_page.attach_obs(mth)

    def detach_obs(self, mth):
        self.gui.rank_page.detach_obs(mth)

    def destroy(self):
        GameObject.destroy(self)


class RankingGui(GuiColleague):

    def __init__(self, mediator, background_fpath, font, fg_col):
        GuiColleague.__init__(self, mediator)
        self.ranking_texts = []
        self.background_path = background_fpath
        self.font = font
        self.fg_col = fg_col
        self.rank_menu = self.background = None

    @staticmethod
    def set_drv_txt_img(page, i, car_name, pos_x, top, text):
        RankingGui.eng.log_mgr.log('drivers: ' + str([drv.dprops for drv in page.drivers]))
        RankingGui.eng.log_mgr.log('i: %s  - carname: %s - text: %s' % (
            i, car_name, text))
        drv = next(
            driver for driver in page.drivers
            if driver.dprops.car_name == car_name)
        is_player_car = car_name in page.rprops.season_props.player_car_names
        RankingGui.eng.log_mgr.log('%s %s %s %s' % (text % drv.logic.dprops.info.name, car_name, drv.logic.dprops.info.img_idx, is_player_car))
        name = text % drv.logic.dprops.info.name
        if '@' in name: name = name.split('@')[0] + '\1smaller\1@' + name.split('@')[1] + '\2'
        txt = Text(
            name, align='left',
            scale=.072, pos=(pos_x, top - i * .16), font=page.font,
            fg=page.text_fg if is_player_car else page.text_bg)
        gprops = page.rprops.season_props.gameprops
        img = Img(
            gprops.cars_img % car_name,
            pos=(pos_x - .16, top + .02 - i * .16), scale=.074)
        filtervpath = RankingGui.eng.curr_path + \
            'yyagl/assets/shaders/filter.vert'
        with open(filtervpath) as fvs:
            vert = fvs.read()
        drvfpath = RankingGui.eng.curr_path + \
            'yyagl/assets/shaders/drv_car.frag'
        with open(drvfpath) as ffs:
            frag = ffs.read()
        shader = load_shader(vert, frag)
        if shader:
            img.set_shader(shader)
        img.set_transparent()
        t_s = TextureStage('ts')
        t_s.set_mode(TextureStage.MDecal)
        txt_path = gprops.drivers_img.path_sel % drv.logic.dprops.info.img_idx
        img.set_texture(t_s, loader.loadTexture(txt_path))
        return txt, img

    def show(self, rprops, sprops, ranking):
        self.rank_menu = RankingMenu(rprops, sprops, ranking)

    def hide(self):
        self.rank_menu.destroy()

    def attach_obs(self, mth):
        self.rank_menu.attach_obs(mth)

    def detach_obs(self, mth):
        self.rank_menu.detach_obs(mth)

    def destroy(self):
        self.hide()
        self.rank_menu = self.ranking_texts = self.background = None
        GuiColleague.destroy(self)
