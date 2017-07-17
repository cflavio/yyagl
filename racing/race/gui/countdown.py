from direct.gui.OnscreenText import OnscreenText
from yyagl.observer import Subject


class Countdown(Subject):

    def __init__(self, countdown_sfx, font):
        Subject.__init__(self)
        self.countdown_sfx = loader.loadSfx(countdown_sfx)
        self.__countdown_txt = OnscreenText(
            '', pos=(0, 0), scale=.2, fg=(1, 1, 1, 1), font=font)
        self.countdown_cnt = 3
        self.tsk = eng.do_later(1.0, self.process_countdown, pass_tsk=True)

    def process_countdown(self, tsk):
        if self.countdown_cnt >= 0:
            self.countdown_sfx.play()
            txt = str(self.countdown_cnt) if self.countdown_cnt else _('GO!')
            self.__countdown_txt.setText(txt)
            self.countdown_cnt -= 1
            return tsk.again
        self.__countdown_txt.destroy()
        self.notify('on_start_race')

    def destroy(self):
        self.tsk = eng.remove_do_later(self.tsk)
        self.__countdown_txt.destroy()
        Subject.destroy(self)
