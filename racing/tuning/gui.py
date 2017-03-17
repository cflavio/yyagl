from direct.gui.OnscreenImage import OnscreenImage
from yyagl.gameobject import Gui
from yyagl.engine.gui.imgbtn import ImageButton


class TuningGuiProps(object):

    def __init__(
            self, car, background, engine_img, tires_img, suspensions_img):
        self.car = car
        self.background = background
        self.engine_img = engine_img
        self.tires_img = tires_img
        self.suspensions_img = suspensions_img


class TuningGui(Gui):

    def __init__(self, mdt, tuninggui_props):
        Gui.__init__(self, mdt)
        self.props = tuninggui_props

    def show(self):
        self.background = OnscreenImage(
            self.props.background, scale=(1.77778, 1, 1.0))
        self.background.setBin('background', 10)
        self.buttons = [ImageButton(
            scale=.4, pos=(-1.2, 1, .1), frameColor=(0, 0, 0, 0),
            image=self.props.engine_img, command=self.on_btn,
            extraArgs=['engine'])]
        self.buttons += [ImageButton(
            scale=.4, pos=(0, 1, .1), frameColor=(0, 0, 0, 0),
            image=self.props.tires_img, command=self.on_btn,
            extraArgs=['tires'])]
        self.buttons += [ImageButton(
            scale=.4, pos=(1.2, 1, .1), frameColor=(0, 0, 0, 0),
            image=self.props.suspensions_img, command=self.on_btn,
            extraArgs=['suspensions'])]

    def on_btn(self, val):
        tun = self.mdt.logic.tunings[self.props.car]
        setattr(tun, val, getattr(tun, val) + 1)
        self.notify('on_tuning_done')

    def hide(self):
        map(lambda wdg: wdg.destroy(), self.buttons + [self.background])
