from yyagl.gameobject import GameObject
from yyagl.lib.p3d.joystick import P3dJoystickMgr as JoystickMgrLib


class JoystickState:

    def __init__(self):
        self.x = self.y = self.b0 = self.b1 = self.b2 = self.b3 = \
            self.dpad_l = self.dpad_r = self.dpad_u = self.dpad_d = \
            self.trigger_l = self.trigger_r = self.shoulder_l = \
            self.shoulder_r = self.stick_l = self.stick_r = 0
        #TODO: rename bi to btni


class JoystickMgr(GameObject):

    def __init__(self, emulate_keyboard):
        GameObject.__init__(self)
        self.emulate_keyboard = emulate_keyboard
        self.old = [JoystickState() for i in range(3)]
        self.nav = None
        self.is_recording = False
        self.joystick_lib = JoystickMgrLib()
        self.joystick_lib.init_joystick()
        # self.eng.do_later(.01, self.eng.attach_obs, [self.on_frame])
        # eng.event doesn't exist
        if self.emulate_keyboard:
            self.set_keyboard_emulation()

    def set_keyboard_emulation(self):
        for i in range(self.joystick_lib.num_joysticks):
            base.accept('joypad%s-dpad_left-up' % i, self.__keyb_evt, [i, 'left'])
            base.accept('joypad%s-dpad_right-up' % i, self.__keyb_evt, [i, 'right'])
            base.accept('joypad%s-dpad_up-up' % i, self.__keyb_evt, [i, 'up'])
            base.accept('joypad%s-dpad_down-up' % i, self.__keyb_evt, [i, 'down'])
            base.accept('joypad%s-face_a-up' % i, self.__keyb_evt, [i, 'fire'])

    def __keyb_evt(self, i, evt):
        if not self.is_recording and self.nav:
            self.eng.send(getattr(self.nav[i], evt))

    def on_frame(self):
        if not self.emulate_keyboard: return
        for i in range(self.joystick_lib.num_joysticks): self.__process(i)

    def __process(self, i):
        j_x, j_y, btn0, btn1, btn2, btn3, dpad_l, dpad_r, dpad_u, dpad_d, \
            trigger_l, trigger_r, shoulder_l, shoulder_r, stick_l, stick_r = \
            self.joystick_lib.get_joystick(i)
        # if not self.is_recording:
        #     if self.old[i].x <= -.4 <= j_x or self.old[i].dpad_l and \
        #             not dpad_l:
        #         if self.nav and i < len(self.nav) and self.nav[i]:
        #             self.eng.send(self.nav[i].left)
        #     if self.old[i].x >= .4 >= j_x or self.old[i].dpad_r and not dpad_r:
        #         if self.nav and i < len(self.nav) and self.nav[i]:
        #             self.eng.send(self.nav[i].right)
        #     if self.old[i].y >= .4 >= j_y or self.old[i].dpad_d and not dpad_d:
        #         if self.nav and i < len(self.nav) and self.nav[i]:
        #             self.eng.send(self.nav[i].down)
        #     if self.old[i].y <= -.4 <= j_y or self.old[i].dpad_u and not dpad_u:
        #         if self.nav and i < len(self.nav) and self.nav[i]:
        #             self.eng.send(self.nav[i].up)
        # if self.old[i].b0 and not btn0:
        #     if self.nav and i < len(self.nav) and self.nav[i] and \
        #             not self.is_recording:
        #         self.eng.send(self.nav[i].fire)
        #     self.eng.send('joypad%s_face_x' % i)
        # if self.old[i].b1 and not btn1:
        #     self.eng.send('joypad%s_face_y' % i)
        # if self.old[i].b2 and not btn2:
        #     self.eng.send('joypad%s_face_a' % i)
        # if self.old[i].b3 and not btn3:
        #     self.eng.send('joypad%s_face_b' % i)
        # if self.old[i].trigger_l and not trigger_l:
        #     self.eng.send('joypad_trigger_l')
        #     self.eng.send('joypad%s_trigger_l' % i)
        # if self.old[i].trigger_r and not trigger_r:
        #     self.eng.send('joypad_trigger_r')
        #     self.eng.send('joypad%s_trigger_r' % i)
        # if self.old[i].shoulder_l and not shoulder_l:
        #     self.eng.send('joypad_shoulder_l')
        #     self.eng.send('joypad%s_shoulder_l' % i)
        # if self.old[i].shoulder_r and not shoulder_r:
        #     self.eng.send('joypad_shoulder_r')
        #     self.eng.send('joypad%s_shoulder_r' % i)
        # if self.old[i].stick_l and not stick_l:
        #     self.eng.send('joypad_stick_l')
        #     self.eng.send('joypad%s_stick_l' % i)
        # if self.old[i].stick_r and not stick_r:
        #     self.eng.send('joypad_stick_r')
        #     self.eng.send('joypad%s_stick_r' % i)
        self.old[i].x, self.old[i].y, self.old[i].b0, self.old[i].b1, \
            self.old[i].b2, self.old[i].b3, self.old[i].dpad_l, \
            self.old[i].dpad_r, self.old[i].dpad_u, self.old[i].dpad_d, \
            self.old[i].trigger_l, self.old[i].trigger_r, \
            self.old[i].shoulder_l, self.old[i].shoulder_r, \
            self.old[i].stick_l, self.old[i].stick_r = \
            j_x, j_y, btn0, btn1, btn2, btn3, dpad_l, dpad_r, dpad_u, dpad_d, \
            trigger_l, trigger_r, shoulder_l, shoulder_r, stick_l, stick_r

    def get_joystick(self, player_idx):
        x, y, face_a, face_b, face_x, face_y, dpadl, dpadr, dpadu, dpadd, triggl, \
            triggr, shl, shr, st_l, st_r = \
            self.joystick_lib.get_joystick(player_idx)
        jstate = JoystickState()
        jstate.x = x
        jstate.y = y
        jstate.face_a = face_a
        jstate.face_b = face_b
        jstate.face_x = face_x
        jstate.face_y = face_y
        jstate.dpad_l = dpadl
        jstate.dpad_r = dpadr
        jstate.dpad_u = dpadu
        jstate.dpad_d = dpadd
        jstate.trigger_l = triggl
        jstate.trigger_r = triggr
        jstate.shoulder_l = shl
        jstate.shoulder_r = shr
        jstate.stick_l = st_l
        jstate.stick_r = st_r
        return jstate

    def get_joystick_val(self, player_idx, code):
        j_x, j_y, btn0, btn1, btn2, btn3, dpad_l, dpad_r, dpad_u, dpad_d, \
            trigger_l, trigger_r, shoulder_l, shoulder_r, stick_l, stick_r = \
            self.joystick_lib.get_joystick(player_idx)
        code2val = {
            'face_x': btn0,
            'face_y': btn1,
            'face_a': btn2,
            'face_b': btn3,
            'dpad_l': dpad_l,
            'dpad_r': dpad_r,
            'dpad_u': dpad_u,
            'dpad_d': dpad_d,
            'trigger_l': trigger_l,
            'trigger_r': trigger_r,
            'shoulder_l': shoulder_l,
            'shoulder_r': shoulder_r,
            'stick_l': stick_l,
            'stick_r': stick_r}
        return code2val[code]

    def bind_keyboard(self, nav): self.nav = nav

    def unbind_keyboard(self): self.nav = None

    def destroy(self):
        try: self.eng.detach_obs(self.on_frame)
        except KeyError: pass
        # it happens in unit tests since it destroys in the same frame
        # remove this catch when i've refactored the object's building
        # and i don't use the director anymore
        self.joystick_lib.destroy()
        GameObject.destroy(self)
