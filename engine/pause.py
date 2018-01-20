from direct.gui.DirectFrame import DirectFrame
from ..gameobject import Gui, Logic, GameObject, Colleague
from ..facade import Facade
from yyagl.library.panda.pause import PandaPause
LibPause = PandaPause


class PauseGui(Gui):

    def __init__(self, mdt):
        Gui.__init__(self, mdt)
        self.pause_frm = None

    def toggle(self, show_frm=True):
        if not self.mdt.logic._pause.is_paused:
            if show_frm:
                self.pause_frm = DirectFrame(frameColor=(.3, .3, .3, .7),
                                               frameSize=(-1.8, 1.8, -1, 1))
        else:
            if self.pause_frm: self.pause_frm.destroy()

    def destroy(self):
        if self.pause_frm: self.pause_frm = self.pause_frm.destroy()
        Gui.destroy(self)


class PauseLogic(Logic):

    def __init__(self, mdt):
        Logic.__init__(self, mdt)
        self._pause = LibPause()

    def remove_task(self, tsk):
        self._pause.remove_task(tsk)

    def pause(self):
        return self._pause.pause()

    def resume(self):
        return self._pause.resume()

    def toggle(self, show_frm=True):
        self.mdt.gui.toggle(show_frm)
        (self.resume if self._pause.is_paused else self.pause)()

    def destroy(self):
        self._pause.destroy()
        Logic.destroy(self)


class PauseFacade(Facade):

    def __init__(self):
        self._fwd_prop('is_paused', lambda obj: obj.logic._pause.is_paused)


class PauseMgr(GameObject, Colleague, PauseFacade):

    def __init__(self, mdt):
        GameObject.__init__(self)
        Colleague.__init__(self, mdt)
        PauseFacade.__init__(self)
        self.gui = PauseGui(self)
        self.logic = PauseLogic(self)

    def remove_task(self, tsk):
        return self.logic.remove_task(tsk)

    def destroy(self):
        self.gui = self.gui.destroy()
        self.logic = self.logic.destroy()
        PauseFacade.destroy(self)
        GameObject.destroy(self)
        Colleague.destroy(self)
