def has_pygame():
    try:
        import pygame
    except ImportError:
        return False
    return True


if has_pygame():
    import pygame
    from pygame import joystick


class JoystickMgr(object):

    def __init__(self):
        self.joysticks = []
        self.init_joystick()
        self.old_x = self.old_y = self.old_b0 = self.old_b1 = 0
        taskMgr.add(self.__emulate_keyboard, 'emulate keyboard')

    def init_joystick(self):
        if not has_pygame():
            return
        pygame.init()
        joystick.init()
        self.joysticks = [
            joystick.Joystick(x) for x in range(joystick.get_count())]
        map(lambda j_s: j_s.init(), self.joysticks)

    def get_joystick(self):
        if not has_pygame():
            return 0, 0, 0, 0
        for _ in pygame.event.get():
            pass
        if not self.joysticks:
            return 0, 0, 0, 0
        j_s = self.joysticks[0]
        return j_s.get_axis(0), j_s.get_axis(1), j_s.get_button(0), \
            j_s.get_button(1)

    def __emulate_keyboard(self, task):
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
        return task.cont

    @staticmethod
    def destroy(self):
        if has_pygame():
            joystick.quit()
            pygame.quit()
