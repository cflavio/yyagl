from direct.gui.OnscreenImage import OnscreenImage
from yyagl.gameobject import Gui
from yyagl.engine.gui.imgbtn import ImgBtn


class TuningGui(Gui):

    def __init__(self, mdt, sprops):
        Gui.__init__(self, mdt)
        self.buttons = self.background = None
        self.sprops = sprops

    def show(self):
        self.background = OnscreenImage(
            self.sprops.background_fpath, scale=(1.77778, 1, 1))
        self.background.setBin('background', 10)
        bprops = {'scale': .4, 'frameColor': (0, 0, 0, 0),
                  'command': self.on_btn}
        self.buttons = [ImgBtn(
            pos=(-1.2, 1, .1), image=self.sprops.tuning_imgs[0],
            extraArgs=['f_engine'], **bprops)]
        self.buttons += [ImgBtn(
            pos=(0, 1, .1), image=self.sprops.tuning_imgs[1],
            extraArgs=['f_tires'], **bprops)]
        self.buttons += [ImgBtn(
            pos=(1.2, 1, .1), image=self.sprops.tuning_imgs[2],
            extraArgs=['f_suspensions'], **bprops)]

    def on_btn(self, val):
        self.notify('on_tuning_sel', val)

    def hide(self):
        map(lambda wdg: wdg.destroy(), self.buttons + [self.background])
