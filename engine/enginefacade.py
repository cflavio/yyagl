class EngineFacade(object):

    def get_joystick(self):
        return self.event.joystick.get_joystick()

    def attach_obs(self, meth):  # otherwise MRO picks Engine's attach
        return self.event.attach(meth)

    def detach_obs(self, meth):
        return self.event.detach(meth)

    def attach_node(self, node):
        return self.gfx.world_np.attachNewNode(node)

    def particle(self, path, parent, render_parent, pos, timeout):
        return self.gfx.particle(path, parent, render_parent, pos, timeout)

    def find_geoms(self, mesh, name):
        return self.phys.find_geoms(mesh, name)

    def attachRigidBody(self, node):
        return self.phys.world_phys.attachRigidBody(node)

    def removeRigidBody(self, node):
        return self.phys.world_phys.removeRigidBody(node)

    def attachGhost(self, node):
        return self.phys.world_phys.attachGhost(node)

    def removeGhost(self, node):
        return self.phys.world_phys.removeGhost(node)

    def add_collision_obj(self, node):
        self.phys.collision_objs += [node]

    def attachVehicle(self, vehicle):
        return self.phys.world_phys.attachVehicle(vehicle)

    def removeVehicle(self, vehicle):
        return self.phys.world_phys.removeVehicle(vehicle)

    def rayTestClosest(self, top, bottom):
        return self.phys.world_phys.rayTestClosest(top, bottom)

    def rayTestAll(self, top, bottom):
        return self.phys.world_phys.rayTestAll(top, bottom)

    def log(self, msg):
        return self.log_mgr.log(msg)

    def do_later(self, time, meth, args=[]):
        return taskMgr.doMethodLater(time, lambda task: meth(*args), meth.__name__)

    def load_model(self, filename, callback=None, extraArgs=[]):
        dct = {'callback': callback, 'extraArgs': extraArgs} if callback else {}
        return self.gfx.load_model(filename, **dct)

    def load_font(self, font):
        return self.font_mgr.load_font(font)

    @property
    def version(self):
        return self.logic.version

    def play(self, sfx):
        return self.audio.play(sfx)

    def set_amb_lgt(self, col):
        return self.shader_mgr.set_amb_lgt(col)

    def set_dir_lgt(self, col, hpr):
        return self.shader_mgr.set_dir_lgt(col, hpr)

    def clear_lights(self):
        return self.shader_mgr.clear_lights()
