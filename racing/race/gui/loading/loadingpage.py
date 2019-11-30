from panda3d.core import TextNode
from yyagl.lib.gui import Text, Img
from yyagl.engine.gui.page import Page, PageGui, PageFacade
from yyagl.gameobject import GameObject, EventColleague
from yyagl.racing.ranking.gui import RankingGui
from yyagl.racing.player.player import Player, TuningPlayer


class LoadingPageGui(PageGui):

    def __init__(self, mediator, menu, rprops, track_name_transl, ranking, players):
        self.rprops = rprops
        self.track_name_transl = track_name_transl
        self.ranking = ranking
        self._players = players
        PageGui.__init__(self, mediator, menu.gui.menu_props)

    def build(self, back_btn=True):
        self.eng.init_gfx()
        self.font = self.mediator.menu.gui.menu_props.font
        self.text_fg = self.mediator.menu.gui.menu_props.text_active_col
        self.text_bg = self.mediator.menu.gui.menu_props.text_normal_col
        self.text_err_col = self.mediator.menu.gui.menu_props.text_err_col
        self.load_txt = Text(
            _('LOADING...'), scale=.2, pos=(0, .78), font=self.font,
            fg=(.75, .75, .75, 1), wordwrap=12)
        track_number = ''
        if not self.rprops.season_props.single_race:
            track_names = self.rprops.season_props.gameprops.season_tracks
            track_num = track_names.index(self.rprops.track_name) + 1
            track_number = ' (%s/%s)' % (track_num, len(track_names))
        track_txt = Text(
            _('track: ') + self.track_name_transl + track_number,
            scale=.08, pos=(0, .62), font=self.font, fg=self.text_bg,
            wordwrap=12)
        self.set_wld_img()
        self.set_grid()
        self.set_ranking()
        self.set_controls()
        self.set_upgrades()
        self.add_widgets([self.load_txt, track_txt])
        PageGui.build(self, False)

    def set_wld_img(self):
        self.wld_img = Img(
            'assets/tracks/%s/images/loading.txo' % self.rprops.track_name,
            pos=(-.25, -.25), scale=.24, parent=base.a2dTopRight)
        #self.wld_img.set_transparency(True)
        self.add_widgets([self.wld_img])

    def set_grid(self):
        txt = Text(_('Starting grid'), scale=.1, pos=(-1.0, .38),
                           font=self.font, fg=self.text_bg)
        self.add_widgets([txt])
        for i, car_name in enumerate(self.rprops.grid):
            pars = i, car_name, -1.28, .22, str(i + 1) + '. %s', self._players
            txt, img = RankingGui.set_drv_txt_img(self, *pars)
            self.add_widgets([txt, img])

    def set_ranking(self):
        items = self.ranking.carname2points.items()
        sorted_ranking = reversed(sorted(items, key=lambda el: el[1]))
        txt = Text(_('Ranking'), scale=.1, pos=(0, .38),
                           font=self.font, fg=self.text_bg)
        self.add_widgets([txt])
        for i, car in enumerate(sorted_ranking):
            txt, img = RankingGui.set_drv_txt_img(self, i, car[0], -.2,
                                                  .22, str(car[1]) + ' %s', self._players)
            self.add_widgets([txt, img])

    def set_controls(self):
        txt = Text(_('Controls'), scale=.1, pos=(1.0, .38),
                           font=self.font, fg=self.text_bg)
        self.add_widgets([txt])
        #if self.rprops.joysticks[0]:
        #    txt = Text(_('joypad'), scale=.08, pos=(1.0, .22),
        #                       font=self.font, fg=self.text_bg)
        #    self.add_widgets([txt])
        #    return
        if self.eng.joystick_mgr.joystick_lib.num_joysticks == 0:
            self.__cmd_label(_('accelerate'), 'forward', .22)
            self.__cmd_label(_('brake/reverse'), 'rear', .12)
            self.__cmd_label(_('left'), 'left', .02)
            self.__cmd_label(_('right'), 'right', -.08)
            self.__cmd_label(_('fire'), 'fire', -.18)
            self.__cmd_label(_('respawn'), 'respawn', -.28)
        else:
            self.__cmd_label(_('accelerate'), 'forward', .22)
            self.__cmd_label(_('brake/reverse'), 'rear', .12)
            self.__cmd_label(_('fire'), 'fire', .02)
            self.__cmd_label(_('respawn'), 'respawn', -.08)

    def set_upgrades(self):
        txt = Text(_('Upgrades'), scale=.1, pos=(1.0, -.56),
                           font=self.font, fg=self.text_bg)
        self.add_widgets([txt])
        #tuning = self.tuning.car2tuning[
        #    self.rprops.season_props.player_car_names[0]]
        first_human = [
            player for player in self._players
            if player.kind == Player.human][0]
        tuning = TuningPlayer(first_human.tuning.engine, first_human.tuning.tires, first_human.tuning.suspensions)
        txt = Text(
            _('engine: +') + str(tuning.engine),
            align='left', scale=.072, pos=(.8, -.7), font=self.font,
            fg=self.text_bg)
        self.widgets += [txt]
        txt = Text(
            _('tires: +') + str(tuning.tires),
            align='left', scale=.072, pos=(.8, -.8), font=self.font,
            fg=self.text_bg)
        self.widgets += [txt]
        txt = Text(
            _('suspensions: +') + str(tuning.suspensions),
            align='left', scale=.072, pos=(.8, -.9), font=self.font,
            fg=self.text_bg)
        self.widgets += [txt]

    def __cmd_label(self, text, key, pos_z):
        _key = getattr(self.rprops.keys.players_keys[0], key)
        if self.eng.joystick_mgr.joystick_lib.num_joysticks:
            _key = self.rprops.joystick[key + '1']
        txt = Text(
            text + ': ' + self.eng.event.key2desc(_key),  #.decode('utf-8'),
            align='left', scale=.064, pos=(.8, pos_z), font=self.font,
            fg=self.text_bg, wordwrap=24)
        self.widgets += [txt]


class LoadingPageLocalMPGui(LoadingPageGui):

    def set_controls(self):
        txt = Text(_('Controls'), scale=.1, pos=(1.0, .38),
                           font=self.font, fg=self.text_bg)
        self.add_widgets([txt])
        txts = []
        player_car_names = [player.car for player in self._players if player.kind == Player.human]
        for i in range(len(player_car_names)):
            if i < self.eng.joystick_mgr.joystick_lib.num_joysticks:
                keys = ['forward', 'rear', 'fire', 'respawn']
                keys = [self.rprops.joystick[key + str(i + 1)] for key in keys]
                txts += [str(i + 1) + ': ' + ', '.join(keys)]
            else:
                keys = ['forward', 'rear', 'left', 'right', 'fire', 'respawn']
                _keys = [getattr(self.rprops.keys.players_keys[i], key) for key in keys]
                tkeys = [self.eng.event.key2desc(_key) for _key in _keys]
                txts += [str(i + 1) + ': ' + ', '.join(tkeys)]
        txt = '\n'.join(txts)
        txt = Text(txt, scale=.056, pos=(.8, .22), font=self.font,
                       fg=self.text_bg, wordwrap=12, align='left')
        self.add_widgets([txt])


class LoadingPage(Page):

    def __init__(self, rprops, menu, track_name_transl, ranking, players):
        self.rprops = rprops
        self.menu = menu
        gui_cls = LoadingPageLocalMPGui if rprops.season_props.kind == 'localmp' else LoadingPageGui
        GameObject.__init__(self)
        self.event = EventColleague(self)
        self.gui = gui_cls(self, menu, rprops, track_name_transl, ranking, players)
        PageFacade.__init__(self)
        # call Page's __init__

    def destroy(self):
        self.event.destroy()
        self.gui.destroy()
        GameObject.destroy(self)
        PageFacade.destroy(self)
