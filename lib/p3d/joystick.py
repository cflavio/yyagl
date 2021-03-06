from panda3d.core import InputDevice


class P3dJoystickMgr:

    def __init__(self):
        self.joysticks = []
        self.curr_vibration = {}
        self.__is_vibrating = [False, False, False, False]

    def init_joystick(self):
        for i, dev in enumerate(base.devices.getDevices(InputDevice.DeviceClass.gamepad)):
            base.attachInputDevice(dev, prefix='joypad%s' % i)
        taskMgr.add(self._update, 'update joysticks')
        # pygame.init()
        # joystick.init()
        # self.joysticks = [
        #     joystick.Joystick(idx) for idx in range(joystick.get_count())]
        # list(map(lambda joystick: joystick.init(), self.joysticks))

    @property
    def num_joysticks(self):
        return len(base.devices.getDevices(InputDevice.DeviceClass.gamepad))

    @staticmethod
    def get_joystick(player_idx):
        devices = base.devices.getDevices(InputDevice.DeviceClass.gamepad)
        if player_idx > len(devices) - 1:
            return 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
        gamepad = devices[player_idx]
        face_a = gamepad.findButton('face_a')
        face_b = gamepad.findButton('face_b')
        face_x = gamepad.findButton('face_x')
        face_y = gamepad.findButton('face_y')
        dpad_l = gamepad.findButton('dpad_left')
        dpad_r = gamepad.findButton('dpad_right')
        dpad_u = gamepad.findButton('dpad_up')
        dpad_d = gamepad.findButton('dpad_down')
        trigger_l = gamepad.findButton('ltrigger')
        trigger_r = gamepad.findButton('rtrigger')
        shoulder_l = gamepad.findButton('lshoulder')
        shoulder_r = gamepad.findButton('rshoulder')
        stick_l = gamepad.findButton('lstick')
        stick_r = gamepad.findButton('rstick')
        left_x = gamepad.findAxis(InputDevice.Axis.left_x)
        left_y = gamepad.findAxis(InputDevice.Axis.left_y)
        trigger_l_axis = gamepad.findAxis(InputDevice.Axis.left_trigger)
        trigger_r_axis = gamepad.findAxis(InputDevice.Axis.right_trigger)
        trigger_l_known = trigger_l.known
        trigger_r_known = trigger_r.known
        return (left_x.value, -left_y.value, face_a.pressed, face_b.pressed,
                face_x.pressed, face_y.pressed,
                dpad_l.pressed, dpad_r.pressed, dpad_u.pressed, dpad_d.pressed,
                trigger_l.pressed or trigger_l_axis.value > .5,
                trigger_r.pressed or trigger_r_axis.value > .5,
                shoulder_l.pressed, shoulder_r.pressed, stick_l.pressed,
                stick_r.pressed, trigger_l_known, trigger_r_known)
        # for _ in pygame.event.get(): pass
        # if not self.joysticks: return 0, 0, 0, 0
        # jstick = self.joysticks[0]
        # axis, btn = jstick.get_axis, jstick.get_button
        # return axis(0), axis(1), btn(0), btn(1)

    def set_vibration(self, player_idx, code, time=-1):
        devices = base.devices.getDevices(InputDevice.DeviceClass.gamepad)
        if player_idx < 0 or player_idx > len(devices) - 1: return
        if player_idx in self.curr_vibration and \
               code in self.curr_vibration[player_idx]: return
        if player_idx not in self.curr_vibration:
            self.curr_vibration[player_idx] = {}
        self.curr_vibration[player_idx][code] = time

    def clear_vibration(self, player_idx, code=None):
        devices = base.devices.getDevices(InputDevice.DeviceClass.gamepad)
        if player_idx < 0 or player_idx > len(devices) - 1: return
        if player_idx not in self.curr_vibration or \
           code not in self.curr_vibration[player_idx]: return
        if code is None: del self.curr_vibration[player_idx]
        else: del self.curr_vibration[player_idx][code]

    def _update(self, task):
        devices = base.devices.getDevices(InputDevice.DeviceClass.gamepad)
        for player_idx in self.curr_vibration:
            for code in self.curr_vibration[player_idx]:
                if self.curr_vibration[player_idx][code] != -1:
                    dt = globalClock.getDt()
                    self.curr_vibration[player_idx][code] -= dt
        for player_idx in self.curr_vibration:
            for code in list(self.curr_vibration[player_idx])[:]:
                if self.curr_vibration[player_idx][code] != -1:
                    if self.curr_vibration[player_idx][code] < 0:
                        del self.curr_vibration[player_idx][code]
        for player_idx in list(self.curr_vibration)[:]:
            if not self.curr_vibration[player_idx]:
                del self.curr_vibration[player_idx]
        for player_idx, dev in enumerate(devices):
            gamepad = devices[player_idx]
            if player_idx in self.curr_vibration and \
                    not self.__is_vibrating[player_idx]:
                gamepad.set_vibration(.2, .4)
                self.__is_vibrating[player_idx] = True
            elif player_idx not in self.curr_vibration:
                gamepad.set_vibration(0, 0)
                self.__is_vibrating[player_idx] = False
        return task.cont

    def destroy(self):
        pass
        # joystick.quit()
        # pygame.quit()
        # self.joysticks = []
