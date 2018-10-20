from panda3d.bullet import BulletWorld, BulletDebugNode, \
    BulletTriangleMesh as BTriangleMesh, \
    BulletTriangleMeshShape as BTriangleMeshShape, \
    BulletRigidBodyNode as BRigidBodyNode, \
    BulletGhostNode as BGhostNode


class BulletPhysWorld(object):

    def __init__(self):
        self.wld = BulletWorld()
        self.__debug_np = None

    def set_gravity(self, vec): return self.wld.set_gravity(vec)

    def init_debug(self):
        debug_node = BulletDebugNode('Debug')
        debug_node.show_bounding_boxes(True)
        self.__debug_np = render.attach_new_node(debug_node)
        self.wld.set_debug_node(self.__debug_np.node())

    def stop(self):
        self.__debug_np.remove_node()

    def attach_rigid_body(self, node): return self.wld.attach_rigid_body(node)

    def remove_rigid_body(self, node): return self.wld.remove_rigid_body(node)

    def attach_ghost(self, node): return self.wld.attach_ghost(node)

    def remove_ghost(self, node): return self.wld.remove_ghost(node)

    def attach_vehicle(self, node): return self.wld.attach_vehicle(node)

    def remove_vehicle(self, node): return self.wld.remove_vehicle(node)

    def ray_test_all(self, a, b, mask=None):
        args = [a.vec, b.vec]
        if mask: args += [mask]
        return self.wld.ray_test_all(*args)

    def ray_test_closest(self, pt_a, pt_b, mask=None):
        args = [pt_a, pt_b]
        if mask: args += [mask]
        return self.wld.ray_test_closest(*args)

    def do_physics(self, dt, num_substeps, size_substeps):
        return self.wld.do_physics(dt, num_substeps, size_substeps)

    def get_contacts(self, node):
        contacts = self.wld.contact_test(node).get_contacts()
        return [BulletContact(contact) for contact in contacts]

    def toggle_debug(self):
        is_hidden = self.__debug_np.is_hidden()
        (self.__debug_np.show if is_hidden else self.__debug_np.hide)()


class BulletContact(object):

    def __init__(self, contact):
        self.contact = contact

    def get_node0(self): return self.contact.get_node0()

    def get_node1(self): return self.contact.get_node1()


class BulletTriangleMesh(object):

    def __init__(self):
        self.mesh = BTriangleMesh()

    def add_geom(self, geom, remove_duplicates, transform):
        return self.mesh.add_geom(geom, remove_duplicates, transform)


class BulletTriangleMeshShape(object):

    def __init__(self, mesh, dynamic):
        self.mesh_shape = BTriangleMeshShape(mesh.mesh, dynamic=dynamic)


class BulletRigidBodyNode(object):

    def __init__(self, name):
        self.node = BRigidBodyNode(name)


class BulletGhostNode(object):

    def __init__(self, name):
        self.node = BGhostNode(name)
