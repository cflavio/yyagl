from panda3d.core import TextNode, Shader, TextureStage
from direct.gui.OnscreenText import OnscreenText
from direct.gui.OnscreenImage import OnscreenImage
from yyagl.engine.gui.page import Page, PageGui, PageFacade
from yyagl.gameobject import GameObject, Event


class LoadingPageGui(PageGui):

    def __init__(self, mdt, menu, rprops, sprops, track_name_transl, drivers):
        self.rprops = rprops
        self.sprops = sprops
        self.track_name_transl = track_name_transl
        self.drivers = drivers
        PageGui.__init__(self, mdt, menu)

    def bld_page(self):
        eng.init_gfx()
        self.font = self.mdt.menu.gui.menu_args.font
        self.text_fg = self.mdt.menu.gui.menu_args.text_fg
        self.text_bg = self.mdt.menu.gui.menu_args.text_bg
        self.text_err = self.mdt.menu.gui.menu_args.text_err
        self.load_txt = OnscreenText(
            text=_('LOADING...'), scale=.2, pos=(0, .72), font=self.font,
            fg=(.75, .75, .75, 1), wordwrap=12)
        track_number = ''
        if not self.sprops.single_race:
            track_names = self.sprops.track_names
            track_num = track_names.index(self.rprops.track_name) + 1
            track_number = ' (%s/%s)' % (track_num, len(track_names))
        track_txt = OnscreenText(
            text=_('track: ') + self.track_name_transl + track_number,
            scale=.08, pos=(0, .56), font=self.font, fg=self.text_bg,
            wordwrap=12)
        self.set_grid()
        self.set_ranking()
        self.set_controls()
        map(self.add_widget, [self.load_txt, track_txt])
        PageGui.bld_page(self, False)

    def set_grid(self):
        txt = OnscreenText(text=_('Starting grid'), scale=.1, pos=(-1.0, .3),
                           font=self.font, fg=self.text_bg)
        self.add_widget(txt)
        for i, car_name in enumerate(self.rprops.grid):
            pars = i, car_name, -1.28, .1, str(i + 1) + '. %s'
            txt, img = LoadingPageGui.set_drv_txt_img(self, *pars)
            map(self.add_widget, [txt, img])

    @staticmethod
    def set_drv_txt_img(page, i, car_name, pos_x, top, text):
        idx, drvname, _, _ = next(
            driver for driver in page.drivers if driver[3] == car_name)
        is_player_car = car_name == page.rprops.player_car_name
        txt = OnscreenText(
            text=text % drvname, align=TextNode.A_left, scale=.072,
            pos=(pos_x, top - i * .16), font=page.font,
            fg=page.text_fg if is_player_car else page.text_bg)
        img = OnscreenImage(
            page.rprops.cars_imgs % car_name,
            pos=(pos_x - .16, 1, top + .02 - i * .16), scale=.074)
        filtervpath = eng.curr_path + 'yyagl/assets/shaders/filter.vert'
        with open(filtervpath) as fvs:
            vert = fvs.read()
        drvfpath = eng.curr_path + 'yyagl/assets/shaders/drv_car.frag'
        with open(drvfpath) as ffs:
            frag = ffs.read()
        shader = Shader.make(Shader.SL_GLSL, vert, frag)
        img.set_shader(shader)
        img.set_transparency(True)
        t_s = TextureStage('ts')
        t_s.set_mode(TextureStage.MDecal)
        txt_path = page.rprops.drivers_img % idx
        img.set_texture(t_s, loader.loadTexture(txt_path))
        return txt, img

    def set_ranking(self):
        items = game.logic.season.ranking.carname2points.items()
        sorted_ranking = reversed(sorted(items, key=lambda el: el[1]))
        txt = OnscreenText(text=_('Ranking'), scale=.1, pos=(0, .3),
                           font=self.font, fg=self.text_bg)
        self.add_widget(txt)
        for i, car in enumerate(sorted_ranking):
            txt, img = LoadingPageGui.set_drv_txt_img(self, i, car[0], -.2, .1,
                                                      str(car[1]) + ' %s')
            map(self.add_widget, [txt, img])

    def set_controls(self):
        txt = OnscreenText(text=_('Controls'), scale=.1, pos=(1.0, .3),
                           font=self.font, fg=self.text_bg)
        self.add_widget(txt)
        if self.rprops.joystick:
            txt = OnscreenText(text=_('joypad'), scale=.08, pos=(1.0, .1),
                               font=self.font, fg=self.text_bg)
            self.add_widget(txt)
            return
        self.__cmd_label(_('accelerate'), 'forward', .1)
        self.__cmd_label(_('brake/reverse'), 'rear', -.06)
        self.__cmd_label(_('left'), 'left', -.22)
        self.__cmd_label(_('right'), 'right', -.38)
        self.__cmd_label(_('fire'), 'button', -.54)
        self.__cmd_label(_('respawn'), 'respawn', -.7)

    def __cmd_label(self, text, key, pos_z):
        txt = OnscreenText(
            text=text + ': ' + self.rprops.keys[key], align=TextNode.A_left,
            scale=.072, pos=(.8, pos_z), font=self.font, fg=self.text_bg)
        self.widgets += [txt]


class LoadingPage(Page):

    def __init__(self, rprops, sprops, menu, track_name_transl, drivers):
        self.rprops = rprops
        self.menu = menu
        init_lst = [
            [('event', Event, [self])],
            [('gui', LoadingPageGui, [self, menu, rprops, sprops,
                                      track_name_transl, drivers])]]
        GameObject.__init__(self, init_lst)
        PageFacade.__init__(self)
