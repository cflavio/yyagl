from ..gameobject import EventColleague
from .joystick import JoystickMgr


class EngineEvent(EventColleague):

    def __init__(self, mediator, emulate_keyboard):
        EventColleague.__init__(self, mediator)
        self.eng.add_task(self.__on_frame)
        if self.eng.lib.version().startswith('1.10'):
            taskMgr.setupTaskChain('unpausable')
            mth = self.__on_frame_unpausable
            taskMgr.add(mth, 'unpausable', taskChain='unpausable')
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
        EventColleague.destroy(self)
