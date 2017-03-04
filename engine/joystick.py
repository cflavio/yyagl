def has_pygame():
    try:
        import pygame
    except ImportError:
        return False
    return True


if has_pygame():
    import pygame
    from pygame import joystick


class JoystickMgrBase(object):

    @staticmethod
    def build(emul_keyb):
        return (JoystickMgr if has_pygame() else JoystickMgrBase)(emul_keyb)

    def __init__(self, emulate_keyboard):
        self.emulate_keyboard = emulate_keyboard
        self.joysticks = []
        self.old_x = self.old_y = self.old_b0 = self.old_b1 = 0
        taskMgr.doMethodLater(.01, lambda task: self.init_joystick(),
                              'init joystick')  # eng.event doesn't exist

    def init_joystick(self):
        pass

    def get_joystick(self):
        return 0, 0, 0, 0

    def destroy(self):
        pass


class JoystickMgr(JoystickMgrBase):

    def init_joystick(self):
        JoystickMgrBase.init_joystick(self)
        pygame.init()
        joystick.init()
        self.joysticks = [
            joystick.Joystick(x) for x in range(joystick.get_count())]
        map(lambda j_s: j_s.init(), self.joysticks)
        eng.event.attach(self.on_frame)

    def get_joystick(self):
        for _ in pygame.event.get():
            pass
        if not self.joysticks:
            return 0, 0, 0, 0
        j_s = self.joysticks[0]
        return j_s.get_axis(0), j_s.get_axis(1), j_s.get_button(0), \
            j_s.get_button(1)

    def on_frame(self):
        if not self.emulate_keyboard:
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
        eng.event.detach(self.on_frame)
        joystick.quit()
        pygame.quit()
        JoystickMgrBase.destroy(self)