from ..gameobject import EventColleague
from .joystick import JoystickMgr


class EngineEvent(EventColleague):

    def __init__(self, mediator, emulate_keyboard):
        EventColleague.__init__(self, mediator)
        self.eng.add_task(self.__on_frame)
        if self.eng.lib.version.startswith('1.10'):
            taskMgr.setupTaskChain('unpausable')
            mth = self.__on_frame_unpausable
            taskMgr.add(mth, 'unpausable', taskChain='unpausable')
        self.joystick_mgr = JoystickMgr(emulate_keyboard)

    def __on_frame(self, task):  # unused task
        self.notify('on_start_frame')
        self.notify('on_frame')
        self.notify('on_end_frame')
        return self.eng.lib.task_cont

    def __on_frame_unpausable(self, task):
        self.notify('on_frame_unpausable')
        return task.cont

    @staticmethod
    def key2desc(keystr):
        if not keystr.startswith('raw-'): return keystr
        keystr = keystr[4:]
        map = base.win.get_keyboard_map()
        virt_key = map.get_mapped_button(keystr)
        return (map.get_mapped_button_label(keystr) or str(virt_key)).lower()

    @staticmethod
    def desc2key(desc):
        map = base.win.get_keyboard_map()
        for i in range(map.get_num_buttons()):
            if map.get_mapped_button_label(i).lower() == desc:
                return map.get_mapped_button(i)

    def destroy(self):
        self.joystick_mgr.destroy()
        EventColleague.destroy(self)
