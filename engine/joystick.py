from yyagl.gameobject import GameObject
from yyagl.library.pygamelib.pygamelib import PygameJoystickMgr as JoystickMgrLib


class JoystickMgr(GameObject):

    def __init__(self, emulate_keyboard):
        GameObject.__init__(self)
        self.emulate_keyboard = emulate_keyboard
        self.old_x = self.old_y = self.old_b0 = self.old_b1 = 0
        self.joystick_lib = JoystickMgrLib.build()
        self.joystick_lib.init_joystick()
        self.eng.do_later(.01, self.eng.attach_obs, [self.on_frame])
        # eng.event doesn't exist

    def on_frame(self):
        if not self.emulate_keyboard: return
        j_x, j_y, btn0, btn1 = self.joystick_lib.get_joystick()
        if self.old_x <= -.4 <= j_x: self.eng.send('arrow_left-up')
        if self.old_x >= .4 >= j_x: self.eng.send('arrow_right-up')
        if self.old_y >= .4 >= j_y: self.eng.send('arrow_down-up')
        if self.old_y <= -.4 <= j_y: self.eng.send('arrow_up-up')
        if self.old_b0 and not btn0: self.eng.send('enter-up')
        self.old_x, self.old_y, self.old_b0, self.old_b1 = j_x, j_y, btn0, btn1

    def get_joystick(self): return self.joystick_lib.get_joystick()

    @staticmethod
    def has_support(): return JoystickMgrLib.has_support()

    def destroy(self):
        self.eng.detach_obs(self.on_frame)
        self.joystick_lib.destroy()
        GameObject.destroy(self)
