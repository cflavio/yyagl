import sys
from ..gameobject import Event
from .joystick import JoystickMgr


class EngineEvent(Event):

    def __init__(self, mdt, emulate_keyboard):
        Event.__init__(self, mdt)
        self.eng.add_task(self.__on_frame)

        # doesn't work on 1.9.2
        #taskMgr.setupTaskChain('unpausable')
        #taskMgr.add(self.__on_frame_unpausable, 'unpausable', taskChain='unpausable')

        self.joystick_mgr = JoystickMgr(emulate_keyboard)

    def __on_frame(self, task):
        self.notify('on_start_frame')
        self.notify('on_frame')
        self.notify('on_end_frame')
        return self.eng.lib.task_cont

    def __on_frame_unpausable(self, task):
        self.notify('on_frame_unpausable')
        return task.cont

    def destroy(self):
        self.joystick_mgr.destroy()
        Event.destroy(self)
