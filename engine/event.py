import sys
from ..gameobject import Event
from .joystick import JoystickMgr


class EngineEventBase(Event):

    @staticmethod
    def init_cls():
        return EngineEvent if eng.base.win else EngineEventBase

    def __init__(self, mdt, emulate_keyboard, on_end_cb):
        Event.__init__(self, mdt)
        self.on_end_cb = on_end_cb
        self.accept('window-closed', self.__on_end)
        taskMgr.add(self.__on_frame, 'on frame')
        JoystickMgr.build(emulate_keyboard)

    def __on_end(self):
        eng.base.closeWindow(eng.base.win)
        self.on_end_cb()
        sys.exit()

    def __on_frame(self, task):
        self.notify('on_start_frame')
        self.notify('on_frame')
        self.notify('on_end_frame')
        return task.cont

    def destroy(self):
        JoystickMgr().destroy()
        Event.destroy(self)


class EngineEvent(EngineEventBase):

    def __init__(self, mdt, emulate_keyboard, on_end_cb):
        EngineEventBase.__init__(self, mdt, emulate_keyboard, on_end_cb)
        eng.base.win.setCloseRequestEvent('window-closed')
