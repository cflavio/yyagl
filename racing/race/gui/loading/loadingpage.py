from os.path import exists
from panda3d.core import TextNode, Shader, TextureStage
from direct.gui.OnscreenText import OnscreenText
from direct.gui.OnscreenImage import OnscreenImage
from yyagl.engine.gui.page import Page, PageGui
from yyagl.gameobject import GameObjectMdt, Event


frag = '''#version 130
in vec2 texcoord;
uniform sampler2D p3d_Texture0;
uniform sampler2D p3d_Texture1;
out vec4 p3d_FragColor;

void main() {
    float dist_l = texcoord.x;
    float dist_r = 1 - texcoord.x;
    float dist_u = texcoord.y;
    float dist_b = 1 - texcoord.y;
    float alpha = min(dist_l, min(dist_r, min(dist_u, dist_b))) * 30;
    vec4 pix_a = texture(p3d_Texture0, texcoord);
    vec4 pix_b = texture(p3d_Texture1, texcoord);
    vec4 tex_col = mix(pix_a, pix_b, pix_b.a);
    p3d_FragColor = tex_col * vec4(1, 1, 1, alpha);
}'''


class LoadingPageGui(PageGui):

    def __init__(
            self, mdt, menu, track_path, car_path, drivers, tracks,
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
        PageGui.__init__(self, mdt, menu)

    def build_page(self):
        eng.gfx.init()
        self.font = self.menu.gui.menu_args.font
        self.text_fg = self.menu.gui.menu_args.text_fg
        self.text_bg = self.menu.gui.menu_args.text_bg
        self.load_txt = OnscreenText(
            text=_('LOADING...'), scale=.2, pos=(0, .72), font=self.font,
            fg=(.75, .75, .75, 1), wordwrap=12)
        track_number = ''
        if not self.single_race:
            track_num = self.tracks.index(self.track_path[7:]) + 1
            track_number = ' (%s/2)' % track_num
        track_txt = OnscreenText(
            text=_('track: ') + self.track_name_transl + track_number,
            scale=.08, pos=(0, .56), font=self.font, fg=self.text_bg,
            wordwrap=12)
        self.set_grid()
        self.set_ranking()
        self.set_controls()
        self.set_first_loading()
        self.widgets += [self.load_txt, track_txt]
        PageGui.build_page(self, False)

    def set_grid(self):
        txt = OnscreenText(
            text=_('Starting grid'), scale=.1, pos=(-1.0, .3), font=self.font,
            fg=self.text_bg)
        self.widgets += [txt]
        for i, car in enumerate(self.grid):
            idx, name, _car = next(
                driver for driver in self.drivers if driver[2] == car)
            is_car = car == self.car_path
            txt = OnscreenText(
                text=str(i + 1) + '. ' + name, align=TextNode.A_left,
                scale=.072, pos=(-1.28, .1 - i * .16), font=self.font,
                fg=self.text_fg if is_car else self.text_bg)
            self.widgets += [txt]
            img = OnscreenImage(self.cars_path % car,
                                pos=(-1.42, 1, .12 - i * .16), scale=.074)
            self.widgets += [img]
            with open('yyagl/assets/shaders/filter.vert') as ffilter:
                vert = ffilter.read()
            shader = Shader.make(Shader.SL_GLSL, vert, frag)
            img.setShader(shader)
            img.setTransparency(True)
            ts = TextureStage('ts')
            ts.setMode(TextureStage.MDecal)
            txt_path = self.drivers_path % idx
            img.setTexture(ts, loader.loadTexture(txt_path))

    def set_ranking(self):
        items = game.logic.season.logic.ranking.logic.ranking.items()
        sorted_ranking = reversed(sorted(items, key=lambda el: el[1]))
        txt = OnscreenText(text=_('Ranking'), scale=.1, pos=(0, .3),
                           font=self.font, fg=self.text_bg)
        self.widgets += [txt]
        for i, car in enumerate(sorted_ranking):
            idx, name, _car = next(
                driver for driver in self.drivers if driver[2] == car[0])
            is_car = car[0] == self.car_path
            txt = OnscreenText(
                text=str(car[1]) + ' ' + name, align=TextNode.A_left,
                scale=.072, pos=(-.2, .1 - i * .16), font=self.font,
                fg=self.text_fg if is_car else self.text_bg)
            self.widgets += [txt]
            img = OnscreenImage(self.cars_path % car[0],
                                pos=(-.36, 1, .12 - i * .16), scale=.074)
            self.widgets += [img]
            with open('yyagl/assets/shaders/filter.vert') as ffilter:
                vert = ffilter.read()
            shader = Shader.make(Shader.SL_GLSL, vert, frag)
            img.setShader(shader)
            img.setTransparency(True)
            ts = TextureStage('ts')
            ts.setMode(TextureStage.MDecal)
            txt_path = self.drivers_path % idx
            img.setTexture(ts, loader.loadTexture(txt_path))

    def set_controls(self):
        txt = OnscreenText(text=_('Controls'), scale=.1, pos=(1.0, .3),
                           font=self.font, fg=self.text_bg)
        self.widgets += [txt]
        if self.joystick:
            txt = OnscreenText(text=_('joypad'), scale=.08, pos=(1.0, .1),
                               font=self.font, fg=self.text_bg)
            self.widgets += [txt]
            return
        txt = OnscreenText(
            text=_('accelerate') + ': ' + self.keys['forward'],
            align=TextNode.A_left, scale=.072, pos=(.8, .1), font=self.font,
            fg=self.text_bg)
        self.widgets += [txt]
        txt = OnscreenText(
            text=_('brake/reverse') + ': ' + self.keys['rear'],
            align=TextNode.A_left, scale=.072, pos=(.8, -.06), font=self.font,
            fg=self.text_bg)
        self.widgets += [txt]
        txt = OnscreenText(
            text=_('left') + ': ' + self.keys['left'], align=TextNode.A_left,
            scale=.072, pos=(.8, -.22), font=self.font, fg=self.text_bg)
        self.widgets += [txt]
        txt = OnscreenText(
            text=_('right') + ': ' + self.keys['right'], align=TextNode.A_left,
            scale=.072, pos=(.8, -.38), font=self.font, fg=self.text_bg)
        self.widgets += [txt]
        txt = OnscreenText(
            text=_('fire') + ': ' + self.keys['button'], align=TextNode.A_left,
            scale=.072, pos=(.8, -.54), font=self.font, fg=self.text_bg)
        self.widgets += [txt]

    def set_first_loading(self):
        vrs = eng.logic.version
        filename = self.track_path[7:] + '_' + vrs + '.bam'
        if exists(filename):
            return
        first_txt = _(
            'We need to elaborate the track on your system (this process '
            'reduces the bandwith required to you for downloading the game), '
            'so you may notice some slowdonws while you play. Everything will '
            'be smoother once the track has been processed!')
        txt = OnscreenText(
            text=first_txt,
            scale=.06, pos=(1.0, .9), font=self.font, fg=(.8, .2, .2, 1),
            bg=(.8, .8, .8, .4), wordwrap=24)
        self.widgets += [txt]

    def destroy(self):
        PageGui.destroy(self)
        eng.base.camera.set_pos(0, 0, 0)
        meth = self.mdt.menu.loading.mdt.event.on_wrong_way
        game.player_car.event.attach(meth)
        meth = self.mdt.menu.loading.mdt.event.on_end_race
        game.player_car.event.attach(meth)


class LoadingPage(Page):

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
        init_lst = [
            [('event', Event, [self])],
            [('gui', LoadingPageGui, [
                self, self.menu, self.track_path, self.car_path, self.drivers,
                self.tracks, self.track_name_transl,
                self.single_race, self.grid, self.cars_path, self.drivers_path,
                self.joystick, self.keys])]]
        GameObjectMdt.__init__(self, init_lst)
