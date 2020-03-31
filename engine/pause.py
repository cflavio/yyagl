from direct.gui.DirectFrame import DirectFrame
from yyagl.gameobject import GuiColleague, LogicColleague, GameObject, Colleague
from yyagl.lib.p3d.pause import P3dPause
LibPause = P3dPause


class PauseGui(GuiColleague):

    def __init__(self, mediator):
        GuiColleague.__init__(self, mediator)
        self.pause_frm = None

    def toggle(self, show_frm=True):
        if not self.mediator.logic._pause.paused:
            if show_frm:
                self.pause_frm = DirectFrame(frameColor=(.3, .3, .3, .7),
                                             frameSize=(-1.8, 1.8, -1, 1))
        else:
            if self.pause_frm: self.pause_frm.destroy()

    def destroy(self):
        if self.pause_frm: self.pause_frm = self.pause_frm.destroy()
        GuiColleague.destroy(self)


class PauseLogic(LogicColleague):

    def __init__(self, mediator):
        LogicColleague.__init__(self, mediator)
        self._pause = LibPause()

    def remove_task(self, tsk):
        self._pause.remove_task(tsk)

    def pause(self):
        self.notify('on_pause')
        return self._pause.pause()

    def resume(self):
        self.notify('on_resume')
        return self._pause.resume()

    def toggle(self, show_frm=True):
        self.mediator.gui.toggle(show_frm)
        (self.resume if self._pause.paused else self.pause)()

    def destroy(self):
        self._pause.destroy()
        LogicColleague.destroy(self)


class PauseFacade:

    @property
    def paused(self): return self.logic._pause.paused


class PauseMgr(GameObject, Colleague, PauseFacade):

    def __init__(self, mediator):
        GameObject.__init__(self)
        Colleague.__init__(self, mediator)
        self.gui = PauseGui(self)
        self.logic = PauseLogic(self)

    def remove_task(self, tsk):
        return self.logic.remove_task(tsk)

    def destroy(self):
        self.gui = self.gui.destroy()
        self.logic = self.logic.destroy()
        GameObject.destroy(self)
        Colleague.destroy(self)
