from ..gameobject import Event
import sys
import pygame
from pygame import joystick


class EngineEvent(Event):

    def __init__(self, mdt):
        Event.__init__(self, mdt)
        self.on_close_cb = lambda: None
        self.accept('window-closed', self.__on_close)
        taskMgr.add(self.__on_frame, 'on frame')
        self.init_joystick()
        self.old_x = self.old_y = self.old_b0 = self.old_b1 = 0

    def init_joystick(self):
        pygame.init()
        joystick.init()
        self.joysticks = [joystick.Joystick(x) for x in range(joystick.get_count())]
        map(lambda j_s: j_s.init(), self.joysticks)

    def get_joystick(self):
        for e in pygame.event.get(): pass
        if not self.joysticks: return 0, 0, 0, 0
        j_s = self.joysticks[0]
        return j_s.get_axis(0), j_s.get_axis(1), j_s.get_button(0), j_s.get_button(1)

    def register_close_cb(self, on_close_cb):
        self.on_close_cb = on_close_cb

    def __on_close(self):
        eng.base.closeWindow(eng.base.win)
        self.on_close_cb()
        sys.exit()

    def __on_frame(self, task):
        self.notify('on_frame')
        self.__emulate_keyboard()
        return task.cont

    def __emulate_keyboard(self):
        if not game.options['development']['menu_joypad']:
            return
        x, y, b0, b1 = self.get_joystick()
        if self.old_x <= -.4 <= x:
            messenger.send('arrow_left-up')
        if self.old_x >= .4 >= x:
            messenger.send('arrow_right-up')
        if self.old_y >= .4 >= y:
            messenger.send('arrow_down-up')
        if self.old_y <= -.4 <= y:
            messenger.send('arrow_up-up')
        if self.old_b0 and not b0:
            messenger.send('enter-up')
        self.old_x, self.old_y, self.old_b0, self.old_b1 = x, y, b0, b1

    def destroy(self):
        Event.destroy(self)
        joystick.quit()
        pygame.quit()


class EngineEventWindow(EngineEvent):

    def __init__(self, mdt):
        EngineEvent.__init__(self, mdt)
        eng.base.win.setCloseRequestEvent('window-closed')
