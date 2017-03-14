from panda3d.core import TextNode, Shader, TextureStage
from direct.gui.OnscreenImage import OnscreenImage
from direct.gui.OnscreenText import OnscreenText
from direct.gui.DirectFrame import DirectFrame
from yyagl.engine.gui.imgbtn import ImageButton
from yyagl.observer import Subject


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


class Results(Subject):

    def __init__(self, menu_args, drivers_imgs, cars_imgs, share_urls,
                 share_imgs):
        Subject.__init__(self)
        self.__res_txts = []
        self.__buttons = []
        self.result_frm = None
        self.menu_args = menu_args
        self.drivers_img = drivers_imgs
        self.cars_imgs = cars_imgs
        self.share_urls = share_urls
        self.share_imgs = share_imgs

    def show(self, race_ranking):
        track = game.track.path  # ref into race
        self.result_frm = DirectFrame(
            frameColor=(.8, .8, .8, .64), frameSize=(-2, 2, -1, 1))
        # race object invokes this
        laps = len(game.player_car.logic.lap_times)  # ref into race
        pars = {'scale': .1, 'fg': self.menu_args.text_bg,
                'font': self.menu_args.font}
        # ref into race
        self.__res_txts = [OnscreenText(
            str(round(game.player_car.logic.lap_times[i], 2)),
            pos=(0, .47 - .2 * (i + 1)), **pars)
            for i in range(laps)]
        self.__res_txts += [OnscreenText(_('LAP'), pos=(-.6, .6), **pars)]
        self.__res_txts += [OnscreenText(_('TIME'), pos=(0, .6), **pars)]
        self.__res_txts += [OnscreenText(_('RANKING'), pos=(.5, .6),
                                         align=TextNode.A_left, **pars)]
        self.__res_txts += [
            OnscreenText(str(i), pos=(-.6, .47 - .2 * i), **pars)
            for i in range(1, 4)]
        race_ranking_sorted = sorted(race_ranking.items(), key=lambda x: x[1])
        race_ranking_sorted = reversed([el[0] for el in race_ranking_sorted])
        drvs = game.fsm.race.logic.drivers
        for i, car in enumerate(race_ranking_sorted):
            idx, name, _car = next(drv for drv in drvs if drv[2] == car)
            is_car = car == game.player_car.name
            fgc = self.menu_args.text_fg if is_car else self.menu_args.text_bg
            txt = OnscreenText(
                text=str(i + 1) + '. ' + name, align=TextNode.A_left,
                scale=.072, pos=(.68, .44 - .16 * (i + 1)),
                font=self.menu_args.font, fg=fgc)
            img = OnscreenImage(self.cars_imgs % car,
                                pos=(.58, 1, .47 - (i + 1) * .16), scale=.074)
            with open('yyagl/assets/shaders/filter.vert') as f:
                vert = f.read()
            shader = Shader.make(Shader.SL_GLSL, vert, frag)
            img.setShader(shader)
            img.setTransparency(True)
            ts = TextureStage('ts')
            ts.setMode(TextureStage.MDecal)
            txt_path = self.drivers_img % idx
            img.setTexture(ts, loader.loadTexture(txt_path))
            self.__res_txts += [txt, img]
        self.__res_txts += [
            OnscreenText(_('share:'), pos=(-.1, -.82), align=TextNode.A_right,
                         **pars)]
        self.__buttons = []

        curr_time = min(game.player_car.logic.lap_times or [0])
        facebook_url = self.share_urls[0]
        #TODO: find a way to share the time on Facebook
        twitter_url = self.share_urls[1]
        twitter_url = twitter_url.format(time=curr_time, track=track)
        plus_url = self.share_urls[2]
        #TODO: find a way to share the time on Google Plus
        tumblr_url = self.share_urls[3]
        #TODO: find a way to share the time on Tumblr
        sites = [('facebook', facebook_url), ('twitter', twitter_url),
                 ('google_plus', plus_url), ('tumblr', tumblr_url)]
        self.__buttons += [
            ImageButton(
                scale=.078,
                pos=(.02 + i*.18, 1, -.79), frameColor=(0, 0, 0, 0),
                image=self.share_imgs % site[0],
                command=eng.gui.open_browser, extraArgs=[site[1]],
                rolloverSound=self.menu_args.rollover,
                clickSound=self.menu_args.click)
            for i, site in enumerate(sites)]

        def step():
            self.notify('on_race_step', race_ranking)
            self.destroy()
            Subject.destroy(self)
        self.tsk = taskMgr.doMethodLater(10.0, lambda tsk: step(), 'step')

    def destroy(self):
        if not self.result_frm or self.result_frm.isEmpty():
            return
        # if it is reached by step then there are two destroys: step's one
        # and race.gui's one
        map(lambda txt: txt.destroy(), self.__res_txts)
        map(lambda btn: btn.destroy(), self.__buttons)
        self.result_frm.destroy()
        self.tsk = taskMgr.remove(self.tsk)
