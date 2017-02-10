from panda3d.core import TextNode, Shader, TextureStage
from direct.gui.OnscreenImage import OnscreenImage
from direct.gui.OnscreenText import OnscreenText
from yyagl.engine.gui.imgbtn import ImageButton
from direct.gui.DirectFrame import DirectFrame


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


class Results(object):

    def __init__(self):
        self.__res_txts = None
        self.__buttons = None
        self.result_frm = None

    def show(self, race_ranking):
        track = game.track.path
        self.result_frm = DirectFrame(frameColor=(.8, .8, .8, .64), frameSize=(-2, 2, -1, 1))
        # race object invokes this
        laps = len(game.player_car.logic.lap_times)
        pars = {'scale': .1, 'fg': (.75, .75, .75, 1),
                'font': eng.font_mgr.load_font('assets/fonts/Hanken-Book.ttf')}
        pars_r = {'scale': .08, 'fg': (.75, .75, .75, 1),
                'font': eng.font_mgr.load_font('assets/fonts/Hanken-Book.ttf')}
        self.__res_txts = [OnscreenText(
            str(round(game.player_car.logic.lap_times[i], 2)),
            pos=(0, .47 - .2 * (i + 1)), **pars)
            for i in range(laps)]
        self.__res_txts += [OnscreenText(_('LAP'), pos=(-.6, .6), **pars)]
        self.__res_txts += [OnscreenText(_('TIME'), pos=(0, .6), **pars)]
        self.__res_txts += [OnscreenText(_('RANKING'), pos=(.5, .6), align=TextNode.A_left, **pars)]
        self.__res_txts += [
            OnscreenText(str(i), pos=(-.6, .47 - .2 * i), **pars)
            for i in range(1, 4)]
        race_ranking_sorted = sorted(race_ranking.items(), key=lambda x: x[1])
        race_ranking_sorted = reversed([el[0] for el in race_ranking_sorted])
        def get_driver(car):
            for driver in game.fsm.race.logic.drivers:
                if driver[2] == car:
                    return driver
        for i, car in enumerate(race_ranking_sorted):
            idx, name, _car = get_driver(car)
            txt = OnscreenText(
                text=str(i + 1) + '. ' + name, align=TextNode.A_left,
                scale=.072, pos=(.68, .44 - .16 * (i + 1)), font=eng.font_mgr.load_font('assets/fonts/Hanken-Book.ttf'),
                fg=(.75, .75, .25, 1) if car == game.player_car.path[5:] else (.75, .75, .75, 1))
            img = OnscreenImage(
                    'assets/images/cars/%s_sel.png' % car,
                    pos=(.58, 1, .47 - (i + 1) * .16), scale=.074)
            shader = Shader.make(Shader.SL_GLSL, vertex=vert, fragment=frag)
            img.setShader(shader)
            img.setTransparency(True)
            ts = TextureStage('ts')
            ts.setMode(TextureStage.MDecal)
            img.setTexture(ts, loader.loadTexture('assets/images/drivers/driver%s_sel.png' % idx))
            self.__res_txts += [txt, img]
        self.__res_txts += [
            OnscreenText(_('share:'), pos=(-.1, -.82), align=TextNode.A_right,
                         **pars)]
        self.__buttons = []

        curr_time = min(game.player_car.logic.lap_times or [0])
        facebook_url = \
            'https://www.facebook.com/sharer/sharer.php?u=ya2.it/yorg'
        #TODO: find a way to share the time on Facebook
        twitter_url = 'https://twitter.com/share?text=' + \
            'I%27ve%20achieved%20{time}%20in%20the%20{track}%20track%20on' + \
            '%20Yorg%20by%20%40ya2tech%21&hashtags=yorg'
        twitter_url = twitter_url.format(time=curr_time, track=track)
        plus_url = 'https://plus.google.com/share?url=ya2.it/yorg'
        #TODO: find a way to share the time on Google Plus
        tumblr_url = 'https://www.tumblr.com/widgets/share/tool?url=ya2.it'
        #TODO: find a way to share the time on Tumblr
        sites = [('facebook', facebook_url), ('twitter', twitter_url),
                 ('google_plus', plus_url), ('tumblr', tumblr_url)]
        self.__buttons += [
            ImageButton(
                scale=.078,
                pos=(.02 + i*.18, 1, -.79), frameColor=(0, 0, 0, 0),
                image='assets/images/icons/%s_png.png' % site[0],
                command=eng.gui.open_browser, extraArgs=[site[1]],
                rolloverSound=loader.loadSfx('assets/sfx/menu_over.wav'),
                clickSound=loader.loadSfx('assets/sfx/menu_clicked.ogg'))
            for i, site in enumerate(sites)]

        def step():
            map(lambda txt: txt.destroy(), self.__res_txts)
            map(lambda btn: btn.destroy(), self.__buttons)
            self.result_frm.destroy()
            #TODO: notify and manage into yorg's fsm
            ranking = game.logic.season.logic.ranking
            tuning = game.logic.season.logic.tuning
            from yyagl.racing.season.season import SingleRaceSeason
            if game.logic.season.__class__ != SingleRaceSeason:
                for car in ranking.logic.ranking:
                    ranking.logic.ranking[car] += race_ranking[car]
                game.options['save']['ranking'] = ranking.logic.ranking
                game.options['save']['tuning'] = tuning.logic.tuning
                game.options.store()
                game.fsm.demand('Ranking')
            else:
                game.fsm.demand('Menu')
        taskMgr.doMethodLater(10.0, lambda tsk: step(), 'step')

    def destroy(self):
        pass
