from ..gameobject import Event
from .joystick import JoystickMgr
import sys


class EngineEventBase(Event):

    @staticmethod
    def init_cls():
        return EngineEvent if eng.base.win else EngineEventBase

    def __init__(self, mdt, emulate_keyboard):
        Event.__init__(self, mdt)
        self.on_close_cb = lambda: None
        self.accept('window-closed', self.__on_close)
        taskMgr.add(self.__on_frame, 'on frame')
        self.joystick = JoystickMgr.build(emulate_keyboard)

    def register_close_cb(self, on_close_cb):
        self.on_close_cb = on_close_cb

    def __on_close(self):
        eng.base.closeWindow(eng.base.win)
        self.on_close_cb()
        sys.exit()

    def __on_frame(self, task):
        self.notify('on_start_frame')
        self.notify('on_frame')
        self.notify('on_end_frame')
        return task.cont

    def destroy(self):
        self.joystick.destroy()
        Event.destroy(self)


class EngineEvent(EngineEventBase):

    def __init__(self, mdt, emulate_keyboard):
        EngineEventBase.__init__(self, mdt, emulate_keyboard)
        eng.base.win.setCloseRequestEvent('window-closed')
