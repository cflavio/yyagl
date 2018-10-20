import pkgutil


def has_pygame():
    return pkgutil.find_loader('pygame') is not None


if has_pygame():
    import pygame
    from pygame import joystick


class PygameJoystickMgrBase(object):  # if there is not pygame

    @staticmethod
    def build():
        return (PygameJoystickMgr if has_pygame() else PygameJoystickMgrBase)()

    def init_joystick(self): pass

    def get_joystick(self): return 0, 0, 0, 0

    @staticmethod
    def supported(): return has_pygame()

    def destroy(self): pass


class PygameJoystickMgr(PygameJoystickMgrBase):

    def __init__(self):
        PygameJoystickMgrBase.__init__(self)
        self.joysticks = []

    def init_joystick(self):
        PygameJoystickMgrBase.init_joystick(self)
        pygame.init()
        joystick.init()
        self.joysticks = [
            joystick.Joystick(idx) for idx in range(joystick.get_count())]
        map(lambda joystick: joystick.init(), self.joysticks)

    def get_joystick(self):
        for _ in pygame.event.get(): pass
        if not self.joysticks: return 0, 0, 0, 0
        jstick = self.joysticks[0]
        axis, btn = jstick.get_axis, jstick.get_button
        return axis(0), axis(1), btn(0), btn(1)

    def destroy(self):
        joystick.quit()
        pygame.quit()
        self.joysticks = []
        PygameJoystickMgrBase.destroy(self)
