from os.path import exists
from panda3d.core import TextNode, Shader, TextureStage
from direct.gui.OnscreenText import OnscreenText
from direct.gui.OnscreenImage import OnscreenImage
from yyagl.engine.gui.page import Page, PageGui
from yyagl.gameobject import GameObjectMdt, Event


class LoadingPageGuiProps(object):

    def __init__(
            self, track_path, car_path, drivers, tracks,
            track_name_transl, single_race, grid, cars_path,
            drivers_path, joystick, keys):
        self.track_path = track_path
        self.car_path = car_path
        self.drivers = drivers
        self.tracks = tracks
        self.track_name_transl = track_name_transl
        self.single_race = single_race
        self.grid = grid
        self.cars_path = cars_path
        self.drivers_path = drivers_path
        self.joystick = joystick
        self.keys = keys


class LoadingPageGui(PageGui):

    def __init__(self, mdt, menu, loadingpagegui_props):
        self.props = loadingpagegui_props
        PageGui.__init__(self, mdt, menu)

    def build_page(self):
        eng.init_gfx()
        self.font = self.menu.gui.menu_args.font
        self.text_fg = self.menu.gui.menu_args.text_fg
        self.text_bg = self.menu.gui.menu_args.text_bg
        self.text_err = self.menu.gui.menu_args.text_err
        self.load_txt = OnscreenText(
            text=_('LOADING...'), scale=.2, pos=(0, .72), font=self.font,
            fg=(.75, .75, .75, 1), wordwrap=12)
        track_number = ''
        if not self.props.single_race:
            track_num = self.props.tracks.index(self.props.track_path) + 1
            track_number = ' (%s/2)' % track_num
        track_txt = OnscreenText(
            text=_('track: ') + self.props.track_name_transl + track_number,
            scale=.08, pos=(0, .56), font=self.font, fg=self.text_bg,
            wordwrap=12)
        self.set_grid()
        self.set_ranking()
        self.set_controls()
        self.set_first_loading()
        self.widgets += [self.load_txt, track_txt]
        PageGui.build_page(self, False)

    def set_grid(self):
        txt = OnscreenText(text=_('Starting grid'), scale=.1, pos=(-1.0, .3),
                           font=self.font, fg=self.text_bg)
        self.widgets += [txt]
        for i, car in enumerate(self.props.grid):
            idx, name, _car, skills = next(
                driver for driver in self.props.drivers if driver[3] == car)
            is_car = car == self.props.car_path
            txt = OnscreenText(
                text=str(i + 1) + '. ' + name, align=TextNode.A_left,
                scale=.072, pos=(-1.28, .1 - i * .16), font=self.font,
                fg=self.text_fg if is_car else self.text_bg)
            self.widgets += [txt]
            img = OnscreenImage(self.props.cars_path % car,
                                pos=(-1.42, 1, .12 - i * .16), scale=.074)
            self.widgets += [img]
            with open('yyagl/assets/shaders/filter.vert') as ffilter:
                vert = ffilter.read()
            with open('yyagl/assets/shaders/drv_car.frag') as f:
                frag = f.read()
            shader = Shader.make(Shader.SL_GLSL, vert, frag)
            img.setShader(shader)
            img.setTransparency(True)
            ts = TextureStage('ts')
            ts.setMode(TextureStage.MDecal)
            txt_path = self.props.drivers_path % idx
            img.setTexture(ts, loader.loadTexture(txt_path))

    def set_ranking(self):
        items = game.logic.season.logic.ranking.logic.ranking.items()
        sorted_ranking = reversed(sorted(items, key=lambda el: el[1]))
        txt = OnscreenText(text=_('Ranking'), scale=.1, pos=(0, .3),
                           font=self.font, fg=self.text_bg)
        self.widgets += [txt]
        for i, car in enumerate(sorted_ranking):
            idx, name, _car, skills = next(
                driver for driver in self.props.drivers if driver[3] == car[0])
            is_car = car[0] == self.props.car_path
            txt = OnscreenText(
                text=str(car[1]) + ' ' + name, align=TextNode.A_left,
                scale=.072, pos=(-.2, .1 - i * .16), font=self.font,
                fg=self.text_fg if is_car else self.text_bg)
            self.widgets += [txt]
            img = OnscreenImage(self.props.cars_path % car[0],
                                pos=(-.36, 1, .12 - i * .16), scale=.074)
            self.widgets += [img]
            with open('yyagl/assets/shaders/filter.vert') as ffilter:
                vert = ffilter.read()
            with open('yyagl/assets/shaders/drv_car.frag') as ffilter:
                frag = ffilter.read()
            shader = Shader.make(Shader.SL_GLSL, vert, frag)
            img.setShader(shader)
            img.setTransparency(True)
            ts = TextureStage('ts')
            ts.setMode(TextureStage.MDecal)
            txt_path = self.props.drivers_path % idx
            img.setTexture(ts, loader.loadTexture(txt_path))

    def set_controls(self):
        txt = OnscreenText(text=_('Controls'), scale=.1, pos=(1.0, .3),
                           font=self.font, fg=self.text_bg)
        self.widgets += [txt]
        if self.props.joystick:
            txt = OnscreenText(text=_('joypad'), scale=.08, pos=(1.0, .1),
                               font=self.font, fg=self.text_bg)
            self.widgets += [txt]
            return
        txt = OnscreenText(
            text=_('accelerate') + ': ' + self.props.keys['forward'],
            align=TextNode.A_left, scale=.072, pos=(.8, .1),
            font=self.font, fg=self.text_bg)
        self.widgets += [txt]
        txt = OnscreenText(
            text=_('brake/reverse') + ': ' + self.props.keys['rear'],
            align=TextNode.A_left, scale=.072, pos=(.8, -.06),
            font=self.font, fg=self.text_bg)
        self.widgets += [txt]
        txt = OnscreenText(
            text=_('left') + ': ' + self.props.keys['left'],
            align=TextNode.A_left, scale=.072, pos=(.8, -.22),
            font=self.font, fg=self.text_bg)
        self.widgets += [txt]
        txt = OnscreenText(
            text=_('right') + ': ' + self.props.keys['right'],
            align=TextNode.A_left, scale=.072, pos=(.8, -.38),
            font=self.font, fg=self.text_bg)
        self.widgets += [txt]
        txt = OnscreenText(
            text=_('fire') + ': ' + self.props.keys['button'],
            align=TextNode.A_left, scale=.072, pos=(.8, -.54),
            font=self.font, fg=self.text_bg)
        self.widgets += [txt]

    def set_first_loading(self):
        filename = self.props.track_path + '_' + eng.version + '.bam'
        if exists(filename):
            return
        first_txt = _(
            'We need to elaborate the track on your system (this process '
            'reduces the bandwith required to you for downloading the game), '
            'so you may notice some slowdonws while you play. Everything will '
            'be smoother once the track has been processed!')
        txt = OnscreenText(
            text=first_txt, scale=.06, pos=(1.0, .9), font=self.font,
            fg=self.text_err, bg=(.8, .8, .8, .4), wordwrap=24)
        self.widgets += [txt]


class LoadingPageProps(object):

    def __init__(
            self, menu, track_path, car_path, drivers, tracks,
            track_name_transl, single_race, grid, cars_path, drivers_path,
            joystick, keys):
        self.menu = menu
        self.track_path = track_path
        self.car_path = car_path
        self.drivers = drivers
        self.tracks = tracks
        self.track_name_transl = track_name_transl
        self.single_race = single_race
        self.grid = grid
        self.cars_path = cars_path
        self.drivers_path = drivers_path
        self.joystick = joystick
        self.keys = keys


class LoadingPage(Page):

    def __init__(self, loadingpage_props):
        l_p = loadingpage_props
        self.props = loadingpage_props
        loadingpagegui_props = LoadingPageGuiProps(
            l_p.track_path, l_p.car_path, l_p.drivers, l_p.tracks,
            l_p.track_name_transl, l_p.single_race, l_p.grid, l_p.cars_path,
            l_p.drivers_path, l_p.joystick, l_p.keys)
        init_lst = [
            [('event', Event, [self])],
            [('gui', LoadingPageGui, [self, l_p.menu, loadingpagegui_props])]]
        GameObjectMdt.__init__(self, init_lst)
