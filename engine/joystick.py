from yyagl.gameobject import GameObject


def has_pygame():
    try:
        import pygame
    except ImportError:
        return False
    return True


if has_pygame():
    import pygame
    from pygame import joystick


class JoystickMgrBase(GameObject):
    # if there is not pygame

    @staticmethod
    def build(emul_keyb):
        return (JoystickMgr if has_pygame() else JoystickMgrBase)(emul_keyb)

    def __init__(self, emulate_keyboard):
        GameObject.__init__(self)
        self.emulate_keyboard = emulate_keyboard
        self.joysticks = []
        self.old_x = self.old_y = self.old_b0 = self.old_b1 = 0
        taskMgr.doMethodLater(.01, lambda tsk: self.init_joystick(),
                              'init joystick')  # eng.event doesn't exist

    def init_joystick(self):
        pass

    def get_joystick(self):
        return 0, 0, 0, 0

    def destroy(self):
        GameObject.destroy(self)


class JoystickMgr(JoystickMgrBase):

    def init_joystick(self):
        JoystickMgrBase.init_joystick(self)
        pygame.init()
        joystick.init()
        self.joysticks = [
            joystick.Joystick(idx) for idx in range(joystick.get_count())]
        map(lambda joystick: joystick.init(), self.joysticks)
        self.eng.attach_obs(self.on_frame)

    def get_joystick(self):
        for _ in pygame.event.get():
            pass
        if not self.joysticks:
            return 0, 0, 0, 0
        jstick = self.joysticks[0]
        return jstick.get_axis(0), jstick.get_axis(1), \
            jstick.get_button(0), jstick.get_button(1)

    def on_frame(self):
        if not self.emulate_keyboard:
            return
        j_x, j_y, btn0, btn1 = self.get_joystick()
        if self.old_x <= -.4 <= j_x:
            messenger.send('arrow_left-up')
        if self.old_x >= .4 >= j_x:
            messenger.send('arrow_right-up')
        if self.old_y >= .4 >= j_y:
            messenger.send('arrow_down-up')
        if self.old_y <= -.4 <= j_y:
            messenger.send('arrow_up-up')
        if self.old_b0 and not btn0:
            messenger.send('enter-up')
        self.old_x, self.old_y, self.old_b0, self.old_b1 = j_x, j_y, btn0, btn1

    def destroy(self):
        self.eng.detach_obs(self.on_frame)
        joystick.quit()
        pygame.quit()
        self.joysticks = None
        JoystickMgrBase.destroy(self)
