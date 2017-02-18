from direct.gui.OnscreenText import OnscreenText
from yyagl.engine.gui.page import Page, PageGui
from direct.gui.DirectFrame import DirectFrame
from direct.gui.DirectGuiGlobals import FLAT
from direct.gui.DirectButton import DirectButton
from yyagl.gameobject import Gui, GameObjectMdt
from yyagl.engine.gui.imgbtn import ImageButton
import sys
from panda3d.core import TextNode, NodePath, Shader, TextureStage, PNMImage,\
    Texture
from direct.gui.OnscreenImage import OnscreenImage
import os


vertexShader = '''
#version 120

uniform mat4 p3d_ModelViewProjectionMatrix;
uniform mat4 p3d_ViewMatrix;
attribute vec4 p3d_Vertex;
attribute vec2 p3d_MultiTexCoord0;
varying vec2 texcoord;
varying vec4 pos;

void main() {
  gl_Position = p3d_ModelViewProjectionMatrix * p3d_Vertex;
  texcoord = p3d_MultiTexCoord0;
  pos = p3d_ViewMatrix * p3d_Vertex;
}'''


textFragmentShader = '''
#version 120

varying vec2 texcoord;
varying vec4 pos;
uniform sampler2D p3d_Texture0;
uniform float ratio;

void main() {
  vec4 mul_color = (pos.x) < ratio - .5 ? vec4(.75, .75, .25, 1) : vec4(.75, .75, .75, .4);
  gl_FragColor = texture2D(p3d_Texture0, texcoord) * mul_color;
}'''


vert = '''#version 130
in vec4 p3d_Vertex;
in vec2 p3d_MultiTexCoord0;
uniform mat4 p3d_ModelViewProjectionMatrix;
out vec2 texcoord;

void main() {
    gl_Position = p3d_ModelViewProjectionMatrix * p3d_Vertex;
    texcoord = p3d_MultiTexCoord0;
}'''


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

    def __init__(self, mdt, menu, track_path, car_path, player_cars, drivers):
        Gui.__init__(self, mdt)
        self.menu = menu
        self.widgets = []
        self.build_page(track_path, car_path, player_cars, drivers)
        self.update_texts()
        self.curr_wdg = None
        self.cnt = 1

    def build_page(self, track_path, car_path, player_cars, drivers):
        menu_gui = self.menu.gui
        eng.gfx.init()
        if not track_path and not car_path:
            tracks = ['prototype', 'desert']
            track = tracks[tracks.index(game.options['save']['track'])]
            track_path = 'tracks/' + track
            car_path = game.options['save']['car']
        conf = game.options
        if 'save' not in conf.dct:
            conf['save'] = {}
        conf['save']['track'] = track_path[7:]
        conf['save']['car'] = car_path
        conf['save']['drivers'] = drivers
        conf.store()
        self.font = eng.font_mgr.load_font('assets/fonts/Hanken-Book.ttf')
        self.load_txt = OnscreenText(
            text=_('LOADING...'),
            scale=.2, pos=(0, .72), font=self.font, fg=(.75, .75, .25, 1),
            wordwrap=12)
        textShader = Shader.make(Shader.SLGLSL, vertexShader, textFragmentShader)
        self.load_txt.setShader(textShader)
        self.load_txt.setShaderInput('ratio', 0)
        track_number = ''
        track_name = track_path[7:]
        track_dct = {
            'prototype': _('prototype'),
            'desert': _('desert')}
        if track_path[7:] in track_dct:
            track_name = track_dct[track_path[7:]]
        from yyagl.racing.season.season import SingleRaceSeason
        if game.logic.season.__class__ != SingleRaceSeason:
            track_num = ['prototype', 'desert'].index(track_path[7:]) + 1
            track_number = ' (%s/2)' % track_num
        track_txt = OnscreenText(
            text=_('track: ') + track_name + track_number,
            scale=.08, pos=(0, .56), font=self.font, fg=(.75, .75, .75, 1),
            wordwrap=12)
        self.set_grid(car_path, drivers)
        self.set_ranking(car_path, drivers)
        self.set_controls()
        self.set_first(track_path)
        self.widgets += [self.load_txt, track_txt]
        PageGui.build_page(self, False)

    def set_grid(self, car_path, drivers):
        grid = ['kronos', 'themis', 'diones', 'iapeto']
        txt = OnscreenText(
            text=_('Starting grid'),
            scale=.1, pos=(-1.0, .3), font=self.font, fg=(.75, .75, .75, 1))
        self.widgets += [txt]
        def get_driver(car):
            for driver in drivers:
                if driver[2] == car:
                    return driver
        for i, car in enumerate(grid):
            idx, name, _car = get_driver(car)
            txt = OnscreenText(
                text=str(i + 1) + '. ' + name, align=TextNode.A_left,
                scale=.072, pos=(-1.28, .1 - i * .16), font=self.font, fg=(.75, .75, .25, 1) if car == car_path else (.75, .75, .75, 1))
            self.widgets += [txt]
            img = OnscreenImage(
                    'assets/images/cars/%s_sel.png' % car,
                    pos=(-1.42, 1, .12 - i * .16), scale=.074)
            self.widgets += [img]
            shader = Shader.make(Shader.SL_GLSL, vert, frag)
            img.setShader(shader)
            img.setTransparency(True)
            ts = TextureStage('ts')
            ts.setMode(TextureStage.MDecal)
            img.setTexture(ts, loader.loadTexture('assets/images/drivers/driver%s_sel.png' % idx))

    def set_ranking(self, car_path, drivers):
        items = game.logic.season.logic.ranking.logic.ranking.items()
        sorted_ranking = reversed(sorted(items, key=lambda el: el[1]))
        txt = OnscreenText(
            text=_('Ranking'),
            scale=.1, pos=(0, .3), font=self.font, fg=(.75, .75, .75, 1))
        self.widgets += [txt]
        def get_driver(car):
            for driver in drivers:
                if driver[2] == car:
                    return driver
        for i, car in enumerate(sorted_ranking):
            idx, name, _car = get_driver(car[0])
            txt = OnscreenText(
                text=str(car[1]) + ' ' + name, align=TextNode.A_left,
                scale=.072, pos=(-.2, .1 - i * .16), font=self.font, fg=(.75, .75, .25, 1) if car[0] == car_path else (.75, .75, .75, 1))
            self.widgets += [txt]
            img = OnscreenImage(
                    'assets/images/cars/%s_sel.png' % car[0],
                    pos=(-.36, 1, .12 - i * .16), scale=.074)
            self.widgets += [img]
            shader = Shader.make(Shader.SL_GLSL, vert, frag)
            img.setShader(shader)
            img.setTransparency(True)
            ts = TextureStage('ts')
            ts.setMode(TextureStage.MDecal)
            img.setTexture(ts, loader.loadTexture('assets/images/drivers/driver%s_sel.png' % idx))

    def set_controls(self):
        items = game.logic.season.logic.ranking.logic.ranking.items()
        sorted_ranking = reversed(sorted(items, key=lambda el: el[1]))
        txt = OnscreenText(
            text=_('Controls'),
            scale=.1, pos=(1.0, .3), font=self.font, fg=(.75, .75, .75, 1))
        self.widgets += [txt]
        conf = game.options
        if conf['settings']['joystick']:
            txt = OnscreenText(
                text=_('joypad'),
                scale=.08, pos=(1.0, .1), font=self.font, fg=(.75, .75, .75, 1))
            self.widgets += [txt]
            return
        txt = OnscreenText(
            text=_('accelerate') + ': ' + conf['settings']['keys']['forward'], align=TextNode.A_left,
            scale=.072, pos=(.8, .1), font=self.font, fg=(.75, .75, .75, 1))
        self.widgets += [txt]
        txt = OnscreenText(
            text=_('brake/reverse') + ': ' + conf['settings']['keys']['rear'], align=TextNode.A_left,
            scale=.072, pos=(.8, -.06), font=self.font, fg=(.75, .75, .75, 1))
        self.widgets += [txt]
        txt = OnscreenText(
            text=_('left') + ': ' + conf['settings']['keys']['left'], align=TextNode.A_left,
            scale=.072, pos=(.8, -.22), font=self.font, fg=(.75, .75, .75, 1))
        self.widgets += [txt]
        txt = OnscreenText(
            text=_('right') + ': ' + conf['settings']['keys']['right'], align=TextNode.A_left,
            scale=.072, pos=(.8, -.38), font=self.font, fg=(.75, .75, .75, 1))
        self.widgets += [txt]
        txt = OnscreenText(
            text=_('fire') + ': ' + conf['settings']['keys']['button'], align=TextNode.A_left,
            scale=.072, pos=(.8, -.54), font=self.font, fg=(.75, .75, .75, 1))
        self.widgets += [txt]

    def set_first(self, track_path):
        filename = track_path[7:] + '_' + eng.logic.version.strip().split()[-1] + '.bam'
        if os.path.exists(filename): return
        first_txt = _(
            'This is the first time that you are playing this track: we are '
            'going to recreate the track on your system, so you may notice '
            'some slowdonws while you play (this process reduces the bandwith '
            "required to you for downloading the game). Everything will be "
            'smoother from the next time!')
        txt = OnscreenText(
            text=first_txt,
            scale=.06, pos=(1.0, .9), font=self.font, fg=(.8, .2, .2, 1),
            bg=(.8, .8, .8, .4), wordwrap=24)
        self.widgets += [txt]

    def on_loading(self, msg):
        names = [model.getName().split('.')[0][5:] for model in game.fsm.race.track.gfx.empty_models]
        names = list(set(list(names)))
        tot = len(names)
        self.load_txt.setShaderInput('ratio', float(self.cnt) / tot)
        self.cnt += 1

    def destroy(self):
        PageGui.destroy(self)
        eng.base.camera.set_pos(0, 0, 0)
        if not hasattr(game, 'player_car'): return
        game.player_car.event.attach(self.mdt.menu.loading.mdt.event.on_wrong_way)
        game.player_car.event.attach(self.mdt.menu.loading.mdt.event.on_end_race)


class LoadingPage(Page):
    gui_cls = LoadingPageGui

    def __init__(self, menu, track_path, car_path, player_cars, drivers):
        self.menu = menu
        self.track_path = track_path
        self.car_path = car_path
        self.player_cars= player_cars
        self.drivers = drivers
        GameObjectMdt.__init__(self, self.init_lst)

    @property
    def init_lst(self):
        return [
            [('fsm', self.fsm_cls, [self])],
            [('gfx', self.gfx_cls, [self])],
            [('phys', self.phys_cls, [self])],
            [('event', self.event_cls, [self])],
            [('gui', self.gui_cls, [self, self.menu, self.track_path, self.car_path, self.player_cars, self.drivers])],
            [('logic', self.logic_cls, [self])],
            [('audio', self.audio_cls, [self])],
            [('ai', self.ai_cls, [self])]]
