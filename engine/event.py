import sys
from ..gameobject import Event
from .joystick import JoystickMgr


class EngineEvent(Event):

    def __init__(self, mdt, emulate_keyboard):
        Event.__init__(self, mdt)
        self.eng.add_task(self.__on_frame)
        self.joystick_mgr = JoystickMgr(emulate_keyboard)

    def __on_frame(self, task):
        self.notify('on_start_frame')
        self.notify('on_frame')
        self.notify('on_end_frame')
        return self.eng.lib.task_cont

    def destroy(self):
        self.joystick_mgr.destroy()
        Event.destroy(self)
