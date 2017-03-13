class EngineFacade(object):

    def get_joystick(self):
        return self.event.joystick.get_joystick()

    def attach_obs(self, meth):  # otherwise MRO picks Engine's attach
        return self.event.attach(meth)

    def detach_obs(self, meth):
        return self.event.detach(meth)
