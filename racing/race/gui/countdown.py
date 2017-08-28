from direct.gui.OnscreenText import OnscreenText
from direct.task.Task import Task
from yyagl.observer import Subject


class Countdown(Subject):

    def __init__(self, sfx_path, font, seconds):
        Subject.__init__(self)
        self.countdown_sfx = loader.loadSfx(sfx_path)
        self.__countdown_txt = OnscreenText(
            '', pos=(0, 0), scale=.2, fg=(1, 1, 1, 1), font=font)
        self.__cnt = seconds
        self.tsk = eng.do_later(1.0, self.process_countdown)

    def process_countdown(self):
        if self.__cnt >= 0:
            self.countdown_sfx.play()
            txt = str(self.__cnt) if self.__cnt else _('GO!')
            self.__countdown_txt.setText(txt)
            self.__cnt -= 1
            return Task.again
        self.__countdown_txt.destroy()
        self.notify('on_start_race')

    def destroy(self):
        self.tsk = eng.remove_do_later(self.tsk)
        self.__countdown_txt.destroy()
        Subject.destroy(self)
