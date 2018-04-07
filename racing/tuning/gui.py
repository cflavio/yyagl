from direct.gui.OnscreenImage import OnscreenImage
from direct.gui.OnscreenText import OnscreenText
from yyagl.gameobject import GuiColleague
from yyagl.engine.gui.imgbtn import ImgBtn
from panda3d.core import TextNode


class TuningGui(GuiColleague):

    def __init__(self, mediator, sprops):
        GuiColleague.__init__(self, mediator)
        self.buttons = self.background = None
        self.sprops = sprops
        self.txt = self.upg1_txt = self.upg2_txt = self.upg3_txt = \
            self.hint1_txt = self.hint2_txt = self.hint3_txt = None

    def show(self):
        self.background = OnscreenImage(
            self.sprops.gameprops.menu_args.background_img,
            scale=(1.77778, 1, 1))
        self.background.setBin('background', 10)
        bprops = {'scale': .4, 'command': self.on_btn}
        self.txt = OnscreenText(
            text=_('What do you want to upgrade?'), scale=.1, pos=(0, .76),
            font=loader.loadFont(self.sprops.font),
            fg=self.sprops.gameprops.menu_args.text_normal)
        self.buttons = [ImgBtn(
            pos=(-1.2, 1, .1), image=self.sprops.tuning_imgs[0],
            extraArgs=['f_engine'], **bprops)]
        self.buttons += [ImgBtn(
            pos=(0, 1, .1), image=self.sprops.tuning_imgs[1],
            extraArgs=['f_tires'], **bprops)]
        self.buttons += [ImgBtn(
            pos=(1.2, 1, .1), image=self.sprops.tuning_imgs[2],
            extraArgs=['f_suspensions'], **bprops)]
        tuning = self.mediator.car2tuning[self.sprops.player_car_name]
        self.upg1_txt = OnscreenText(
            text=_('current upgrades: +') + str(tuning.f_engine),
            scale=.06,
            pos=(-1.53, -.36), font=loader.loadFont(self.sprops.font),
            wordwrap=12, align=TextNode.ALeft,
            fg=self.sprops.gameprops.menu_args.text_normal)
        self.upg2_txt = OnscreenText(
            text=_('current upgrades: +') + str(tuning.f_tires),
            scale=.06,
            pos=(-.35, -.36), font=loader.loadFont(self.sprops.font),
            wordwrap=12, align=TextNode.ALeft,
            fg=self.sprops.gameprops.menu_args.text_normal)
        self.upg3_txt = OnscreenText(
            text=_('current upgrades: +') + str(tuning.f_suspensions),
            scale=.06,
            pos=(.85, -.36), font=loader.loadFont(self.sprops.font),
            wordwrap=12, align=TextNode.ALeft,
            fg=self.sprops.gameprops.menu_args.text_normal)
        self.hint1_txt = OnscreenText(
            text=_("engine: it increases car's maximum speed"),
            scale=.06,
            pos=(-1.53, -.46), font=loader.loadFont(self.sprops.font),
            wordwrap=12, align=TextNode.ALeft,
            fg=self.sprops.gameprops.menu_args.text_normal)
        self.hint2_txt = OnscreenText(
            text=_("tires: they increase car's adherence"),
            scale=.06,
            pos=(-.35, -.46), font=loader.loadFont(self.sprops.font),
            wordwrap=12, align=TextNode.ALeft,
            fg=self.sprops.gameprops.menu_args.text_normal)
        self.hint3_txt = OnscreenText(
            text=_("suspensions: they increase car's stability"),
            scale=.06,
            pos=(.85, -.46), font=loader.loadFont(self.sprops.font),
            wordwrap=12, align=TextNode.ALeft,
            fg=self.sprops.gameprops.menu_args.text_normal)

    def on_btn(self, val):
        self.notify('on_tuning_sel', val)

    def hide(self):
        wdgs = [self.background, self.txt, self.hint1_txt, self.hint2_txt,
                self.hint3_txt, self.upg1_txt, self.upg2_txt,
                self.upg3_txt]
        map(lambda wdg: wdg.destroy(), self.buttons + wdgs)
