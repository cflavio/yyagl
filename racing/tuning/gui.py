from direct.gui.OnscreenImage import OnscreenImage
from yyagl.gameobject import Gui
from yyagl.engine.gui.imgbtn import ImgBtn


class TuningGui(Gui):

    def __init__(self, mdt, tuning_props):
        Gui.__init__(self, mdt)
        self.buttons = self.background = None
        self.props = tuning_props

    def show(self):
        self.background = OnscreenImage(
            self.props.background, scale=(1.77778, 1, 1.0))
        self.background.setBin('background', 10)
        self.buttons = [ImgBtn(
            scale=.4, pos=(-1.2, 1, .1), frameColor=(0, 0, 0, 0),
            image=self.props.tuning_imgs[0], command=self.on_btn,
            extraArgs=['engine'])]
        self.buttons += [ImgBtn(
            scale=.4, pos=(0, 1, .1), frameColor=(0, 0, 0, 0),
            image=self.props.tuning_imgs[1], command=self.on_btn,
            extraArgs=['tires'])]
        self.buttons += [ImgBtn(
            scale=.4, pos=(1.2, 1, .1), frameColor=(0, 0, 0, 0),
            image=self.props.tuning_imgs[2], command=self.on_btn,
            extraArgs=['suspensions'])]

    def on_btn(self, val):
        tun = self.mdt.logic.tunings[self.props.player_car]
        setattr(tun, val, getattr(tun, val) + 1)
        self.notify('on_tuning_done')

    def hide(self):
        map(lambda wdg: wdg.destroy(), self.buttons + [self.background])
