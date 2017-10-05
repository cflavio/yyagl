class PhysWorld(object):

    def __init__(self): pass

    def set_gravity(self, vec): pass

    def init_debug(self): pass

    def stop(self): pass

    def attach_rigid_body(self, node): pass

    def remove_rigid_body(self, node): pass

    def attach_ghost(self, node): pass

    def remove_ghost(self, node): pass

    def attach_vehicle(self, node): pass

    def remove_vehicle(self, node): pass

    def ray_test_all(self, node, mask=None): pass

    def ray_test_closest(self, a, b, mask=None): pass

    def do_physics(self, dt, num_substeps, size_substeps): pass

    def get_contacts(self, node): pass


class Contact(object):

    def __init__(self, contact): pass

    def get_node0(self): pass

    def get_node1(self): pass
