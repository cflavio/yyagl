from panda3d.core import InputDevice


class P3dJoystickMgr:

    def __init__(self):
        self.joysticks = []

    def init_joystick(self):
        for dev in base.devices.getDevices(InputDevice.DeviceClass.gamepad):
            base.attachInputDevice(dev)
        #pygame.init()
        #joystick.init()
        #self.joysticks = [
        #    joystick.Joystick(idx) for idx in range(joystick.get_count())]
        #list(map(lambda joystick: joystick.init(), self.joysticks))

    def get_joystick(self, player_idx):
        devices = base.devices.getDevices(InputDevice.DeviceClass.gamepad)
        if player_idx > len(devices) - 1: return 0, 0, 0, 0
        gamepad = devices[player_idx]
        btn_0 = gamepad.findButton('face_a')
        btn_1 = gamepad.findButton('face_b')
        left_x = gamepad.findAxis(InputDevice.Axis.left_x)
        left_y = gamepad.findAxis(InputDevice.Axis.left_y)
        return left_x.value, -left_y.value, btn_0.pressed, btn_1.pressed
        #for _ in pygame.event.get(): pass
        #if not self.joysticks: return 0, 0, 0, 0
        #jstick = self.joysticks[0]
        #axis, btn = jstick.get_axis, jstick.get_button
        #return axis(0), axis(1), btn(0), btn(1)

    def destroy(self):
        pass
        #joystick.quit()
        #pygame.quit()
        #self.joysticks = []
