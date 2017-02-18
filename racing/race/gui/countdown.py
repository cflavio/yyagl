from direct.gui.OnscreenText import OnscreenText
from yyagl.observer import Subject


class Countdown(Subject):

    def __init__(self):
        Subject.__init__(self)
        self.countdown_sfx = loader.loadSfx('assets/sfx/countdown.ogg')
        self.__countdown_txt = OnscreenText(
            '', pos=(0, 0), scale=.2, fg=(1, 1, 1, 1),
            font=eng.font_mgr.load_font('assets/fonts/Hanken-Book.ttf'))
        self.countdown_cnt = 3
        meth = self.process_countdown
        self.tsk = taskMgr.doMethodLater(1.0, meth, 'coutdown')

    def process_countdown(self, task):
        if self.countdown_cnt >= 0:
            self.countdown_sfx.play()
            txt = str(self.countdown_cnt) if self.countdown_cnt else _('GO!')
            self.__countdown_txt.setText(txt)
            self.countdown_cnt -= 1
            return task.again
        self.__countdown_txt.destroy()
        self.notify('on_start_race')

    def destroy(self):
        Subject.destroy(self)
        taskMgr.remove(self.tsk)
        self.tsk = None
        self.__countdown_txt.destroy()
