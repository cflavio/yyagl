from yyagl.gameobject import GameObject
from yyagl.lib.p3d.joystick import P3dJoystickMgr as JoystickMgrLib


class JoystickMgr(GameObject):

    def __init__(self, emulate_keyboard):
        GameObject.__init__(self)
        self.emulate_keyboard = emulate_keyboard
        self.old_x = self.old_y = self.old_b0 = self.old_b1 = self.old_b2 = self.old_b3 = 0
        self.joystick_lib = JoystickMgrLib()
        self.joystick_lib.init_joystick()
        self.eng.do_later(.01, self.eng.attach_obs, [self.on_frame])
        # eng.event doesn't exist

    def on_frame(self):
        if not self.emulate_keyboard: return
        j_x, j_y, btn0, btn1, btn2, btn3 = self.joystick_lib.get_joystick(0)
        if self.old_x <= -.4 <= j_x: self.eng.send('arrow_left-up')
        if self.old_x >= .4 >= j_x: self.eng.send('arrow_right-up')
        if self.old_y >= .4 >= j_y: self.eng.send('arrow_down-up')
        if self.old_y <= -.4 <= j_y: self.eng.send('arrow_up-up')
        if self.old_b0 and not btn0: self.eng.send('enter-up')
        self.old_x, self.old_y, self.old_b0, self.old_b1, self.old_b2, self.old_b3 = \
            j_x, j_y, btn0, btn1, btn2, btn3

    def get_joystick(self, player_idx):
        return self.joystick_lib.get_joystick(player_idx)

    @staticmethod
    def supported(): return JoystickMgrLib.supported()

    def destroy(self):
        self.eng.detach_obs(self.on_frame)
        self.joystick_lib.destroy()
        GameObject.destroy(self)
