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

    def play(self, sfx):
        return self.audio.play(sfx)