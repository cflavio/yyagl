from yyagl.gameobject import GameObject
from yyagl.lib.p3d.joystick import P3dJoystickMgr as JoystickMgrLib


class JoystickState:

    def __init__(self):
        self.x = self.y = self.b0 = self.b1 = self.b2 = self.b3 = self.dpad_l = self.dpad_r = self.dpad_u = self.dpad_d = 0


class JoystickMgr(GameObject):

    def __init__(self, emulate_keyboard):
        GameObject.__init__(self)
        self.emulate_keyboard = emulate_keyboard
        self.old = [JoystickState() for i in range(3)]
        self.nav = None
        self.joystick_lib = JoystickMgrLib()
        self.joystick_lib.init_joystick()
        self.eng.do_later(.01, self.eng.attach_obs, [self.on_frame])
        # eng.event doesn't exist

    def on_frame(self):
        if not self.emulate_keyboard: return
        for i in range(self.joystick_lib.num_joysticks): self.__process(i)

    def __process(self, i):
        j_x, j_y, btn0, btn1, btn2, btn3, dpad_l, dpad_r, dpad_u, dpad_d = self.joystick_lib.get_joystick(i)
        if self.old[i].x <= -.4 <= j_x or self.old[i].dpad_l and not dpad_l:
            if self.nav and i < len(self.nav) and self.nav[i]: self.eng.send(self.nav[i].left)
        if self.old[i].x >= .4 >= j_x or self.old[i].dpad_r and not dpad_r:
            if self.nav and i < len(self.nav) and self.nav[i]: self.eng.send(self.nav[i].right)
        if self.old[i].y >= .4 >= j_y or self.old[i].dpad_d and not dpad_d:
            if self.nav and i < len(self.nav) and self.nav[i]: self.eng.send(self.nav[i].down)
        if self.old[i].y <= -.4 <= j_y or self.old[i].dpad_u and not dpad_u:
            if self.nav and i < len(self.nav) and self.nav[i]: self.eng.send(self.nav[i].up)
        if self.old[i].b0 and not btn0:
            if self.nav and i < len(self.nav) and self.nav[i]: self.eng.send(self.nav[i].fire)
        if self.old[i].b1 and not btn1:
            self.eng.send('joypad_b1')
        self.old[i].x, self.old[i].y, self.old[i].b0, self.old[i].b1, self.oldb2, self.old[i].b3, self.old[i].dpad_l, self.old[i].dpad_r, self.old[i].dpad_u, self.old[i].dpad_d = \
            j_x, j_y, btn0, btn1, btn2, btn3, dpad_l, dpad_r, dpad_u, dpad_d

    def get_joystick(self, player_idx):
        return self.joystick_lib.get_joystick(player_idx)

    @staticmethod
    def supported(): return JoystickMgrLib.supported()

    def bind_keyboard(self, nav): self.nav = nav

    def unbind_keyboard(self, i): self.nav[i] = None

    def destroy(self):
        self.eng.detach_obs(self.on_frame)
        self.joystick_lib.destroy()
        GameObject.destroy(self)
