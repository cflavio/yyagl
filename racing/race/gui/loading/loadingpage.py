from panda3d.core import TextNode
from direct.gui.OnscreenText import OnscreenText
from direct.gui.OnscreenImage import OnscreenImage
from yyagl.engine.gui.page import Page, PageGui, PageFacade
from yyagl.gameobject import GameObject, Event
from yyagl.racing.ranking.gui import RankingGui


class LoadingPageGui(PageGui):

    def __init__(self, mdt, menu, rprops, track_name_transl, drivers, ranking, tuning):
        self.rprops = rprops
        self.track_name_transl = track_name_transl
        self.drivers = drivers
        self.ranking = ranking
        self.tuning = tuning
        PageGui.__init__(self, mdt, menu)

    def bld_page(self, back_btn=True):
        self.eng.init_gfx()
        self.font = self.mdt.menu.gui.menu_args.font
        self.text_fg = self.mdt.menu.gui.menu_args.text_fg
        self.text_bg = self.mdt.menu.gui.menu_args.text_bg
        self.text_err = self.mdt.menu.gui.menu_args.text_err
        self.load_txt = OnscreenText(
            text=_('LOADING...'), scale=.2, pos=(0, .78), font=self.font,
            fg=(.75, .75, .75, 1), wordwrap=12)
        track_number = ''
        if not self.rprops.season_props.single_race:
            track_names = self.rprops.season_props.gameprops.season_tracks
            track_num = track_names.index(self.rprops.track_name) + 1
            track_number = ' (%s/%s)' % (track_num, len(track_names))
        track_txt = OnscreenText(
            text=_('track: ') + self.track_name_transl + track_number,
            scale=.08, pos=(0, .62), font=self.font, fg=self.text_bg,
            wordwrap=12)
        self.set_wld_img()
        self.set_grid()
        self.set_ranking()
        self.set_controls()
        self.set_upgrades()
        map(self.add_widget, [self.load_txt, track_txt])
        PageGui.bld_page(self, False)

    def set_wld_img(self):
        self.wld_img = OnscreenImage(
            'assets/images/loading/%s.txo' % self.rprops.track_name,
            pos=(-.25, 1, -.25), scale=.24, parent=base.a2dTopRight)
        self.wld_img.set_transparency(True)
        self.add_widget(self.wld_img)

    def set_grid(self):
        txt = OnscreenText(text=_('Starting grid'), scale=.1, pos=(-1.0, .38),
                           font=self.font, fg=self.text_bg)
        self.add_widget(txt)
        for i, car_name in enumerate(self.rprops.grid):
            pars = i, car_name, -1.28, .22, str(i + 1) + '. %s'
            txt, img = RankingGui.set_drv_txt_img(self, *pars)
            map(self.add_widget, [txt, img])

    def set_ranking(self):
        items = self.ranking.carname2points.items()
        sorted_ranking = reversed(sorted(items, key=lambda el: el[1]))
        txt = OnscreenText(text=_('Ranking'), scale=.1, pos=(0, .38),
                           font=self.font, fg=self.text_bg)
        self.add_widget(txt)
        for i, car in enumerate(sorted_ranking):
            txt, img = RankingGui.set_drv_txt_img(self, i, car[0], -.2,
                                                  .22, str(car[1]) + ' %s')
            map(self.add_widget, [txt, img])

    def set_controls(self):
        txt = OnscreenText(text=_('Controls'), scale=.1, pos=(1.0, .38),
                           font=self.font, fg=self.text_bg)
        self.add_widget(txt)
        if self.rprops.joystick:
            txt = OnscreenText(text=_('joypad'), scale=.08, pos=(1.0, .22),
                               font=self.font, fg=self.text_bg)
            self.add_widget(txt)
            return
        self.__cmd_label(_('accelerate'), 'forward', .22)
        self.__cmd_label(_('brake/reverse'), 'rear', .12)
        self.__cmd_label(_('left'), 'left', .02)
        self.__cmd_label(_('right'), 'right', -.08)
        self.__cmd_label(_('fire'), 'fire', -.18)
        self.__cmd_label(_('respawn'), 'respawn', -.28)

    def set_upgrades(self):
        txt = OnscreenText(text=_('Upgrades'), scale=.1, pos=(1.0, -.56),
                           font=self.font, fg=self.text_bg)
        self.add_widget(txt)
        tuning = self.tuning.car2tuning[
            self.rprops.season_props.player_car_name]
        txt = OnscreenText(
            text=_('engine: +') + str(tuning.f_engine),
            align=TextNode.A_left, scale=.072, pos=(.8, -.7), font=self.font,
            fg=self.text_bg)
        self.widgets += [txt]
        txt = OnscreenText(
            text=_('tires: +') + str(tuning.f_tires),
            align=TextNode.A_left, scale=.072, pos=(.8, -.8), font=self.font,
            fg=self.text_bg)
        self.widgets += [txt]
        txt = OnscreenText(
            text=_('suspensions: +') + str(tuning.f_suspensions),
            align=TextNode.A_left, scale=.072, pos=(.8, -.9), font=self.font,
            fg=self.text_bg)
        self.widgets += [txt]

    def __cmd_label(self, text, key, pos_z):
        txt = OnscreenText(
            text=text + ': ' + getattr(self.rprops.keys, key),
            align=TextNode.A_left, scale=.072, pos=(.8, pos_z), font=self.font,
            fg=self.text_bg)
        self.widgets += [txt]


class LoadingPage(Page):

    def __init__(self, rprops, menu, track_name_transl, drivers, ranking, tuning):
        self.rprops = rprops
        self.menu = menu
        init_lst = [
            [('event', Event, [self])],
            [('gui', LoadingPageGui, [self, menu, rprops, track_name_transl,
                                      drivers, ranking, tuning])]]
        GameObject.__init__(self, init_lst)
        PageFacade.__init__(self)
        # call Page's __init__

    def destroy(self):
        GameObject.destroy(self)
        PageFacade.destroy(self)
