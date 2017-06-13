from panda3d.core import TextNode, Shader, TextureStage
from direct.gui.OnscreenImage import OnscreenImage
from direct.gui.OnscreenText import OnscreenText
from direct.gui.DirectFrame import DirectFrame
from yyagl.engine.gui.imgbtn import ImgBtn
from yyagl.observer import Subject
from direct.gui.DirectButton import DirectButton


class ResultProps(object):

    def __init__(self, menu_args, drivers_imgs, cars_imgs, share_urls,
                 share_imgs, track_path):
        self.menu_args = menu_args
        self.drivers_imgs = drivers_imgs
        self.cars_imgs = cars_imgs
        self.share_urls = share_urls
        self.share_imgs = share_imgs
        self.track_path = track_path


class Results(Subject):

    def __init__(self, result_props):
        Subject.__init__(self)
        self.__res_txts = []
        self.__buttons = []
        self.result_frm = None
        self.props = result_props

    def show(self, race_ranking, lap_times, drivers, player_car_name):
        track = self.props.track_path
        self.result_frm = DirectFrame(
            frameColor=(.8, .8, .8, .64), frameSize=(-2, 2, -1, 1))
        laps = len(lap_times)
        text_bg = self.props.menu_args.text_bg
        pars = {'scale': .1, 'fg': text_bg, 'font': self.props.menu_args.font}
        # ref into race
        self.__res_txts = [OnscreenText(
            str(round(lap_times[i], 2)), pos=(0, .47 - .2 * (i + 1)), **pars)
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
        for i, car in enumerate(race_ranking_sorted):
            carinfo = next(drv for drv in drivers if drv[3] == car)
            idx, name, skills, _car = carinfo
            is_car = car == player_car_name
            fgc = self.props.menu_args.text_fg if is_car else text_bg
            txt = OnscreenText(
                text=str(i + 1) + '. ' + name, align=TextNode.A_left,
                scale=.072, pos=(.68, .44 - .16 * (i + 1)),
                font=self.props.menu_args.font, fg=fgc)
            img = OnscreenImage(self.props.cars_imgs % car,
                                pos=(.58, 1, .47 - (i + 1) * .16), scale=.074)
            with open(eng.curr_path + 'yyagl/assets/shaders/filter.vert') as f:
                vert = f.read()
            with open(eng.curr_path + 'yyagl/assets/shaders/drv_car.frag') as f:
                frag = f.read()
            shader = Shader.make(Shader.SL_GLSL, vert, frag)
            img.setShader(shader)
            img.setTransparency(True)
            ts = TextureStage('ts')
            ts.setMode(TextureStage.MDecal)
            txt_path = self.props.drivers_imgs % idx
            img.setTexture(ts, loader.loadTexture(txt_path))
            self.__res_txts += [txt, img]
        self.__res_txts += [
            OnscreenText(_('share:'), pos=(-.1, -.82), align=TextNode.A_right,
                         **pars)]
        self.__buttons = []

        curr_time = min(game.player_car.logic.lap_times or [0])
        facebook_url = self.props.share_urls[0]
        #TODO: find a way to share the time on Facebook
        twitter_url = self.props.share_urls[1]
        twitter_url = twitter_url.format(time=round(curr_time, 2), track=track)
        plus_url = self.props.share_urls[2]
        #TODO: find a way to share the time on Google Plus
        tumblr_url = self.props.share_urls[3]
        #TODO: find a way to share the time on Tumblr
        sites = [('facebook', facebook_url), ('twitter', twitter_url),
                 ('google_plus', plus_url), ('tumblr', tumblr_url)]
        self.__buttons += [
            ImgBtn(
                scale=.078,
                pos=(.02 + i*.18, 1, -.79), frameColor=(0, 0, 0, 0),
                image=self.props.share_imgs % site[0],
                command=eng.open_browser, extraArgs=[site[1]],
                rolloverSound=self.props.menu_args.rollover,
                clickSound=self.props.menu_args.click)
            for i, site in enumerate(sites)]

        def step():
            self.notify('on_race_step', race_ranking)
            self.destroy()
            Subject.destroy(self)
        cont_btn = DirectButton(
            text=_('Continue'), pos=(0, 1, -.6), command=step,
            **self.props.menu_args.btn_args)
        self.__buttons += [cont_btn]

    def destroy(self):
        if not self.result_frm or self.result_frm.isEmpty():
            return
        # if it is reached by step then there are two destroys: step's one
        # and race.gui's one
        map(lambda txt: txt.destroy(), self.__res_txts)
        map(lambda btn: btn.destroy(), self.__buttons)
        self.result_frm.destroy()
