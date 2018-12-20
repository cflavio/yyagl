from panda3d.bullet import BulletWorld as BWorld, \
    BulletDebugNode as BDebugNode, \
    BulletTriangleMesh as BTriangleMesh, \
    BulletTriangleMeshShape as BTriangleMeshShape, \
    BulletRigidBodyNode as BRigidBodyNode, \
    BulletGhostNode as BGhostNode
from yyagl.facade import Facade


class BulletPhysWorld(Facade):

    def __init__(self):
        self.wld = BWorld()
        self.__debug_np = None
        mth_lst = [
            ('attach_rigid_body', lambda obj: obj.wld.attach_rigid_body),
            ('remove_rigid_body', lambda obj: obj.wld.remove_rigid_body),
            ('attach_ghost', lambda obj: obj.wld.attach_ghost),
            ('remove_ghost', lambda obj: obj.wld.remove_ghost),
            ('attach_vehicle', lambda obj: obj.wld.attach_vehicle),
            ('remove_vehicle', lambda obj: obj.wld.remove_vehicle),
            ('ray_test_closest', lambda obj: obj.wld.ray_test_closest)]
        Facade.__init__(self, mth_lst=mth_lst)

    def set_gravity(self, vec): return self.wld.set_gravity(vec)

    def init_debug(self):
        debug_node = BDebugNode('Debug')
        debug_node.show_bounding_boxes(True)
        self.__debug_np = render.attach_new_node(debug_node)
        self.wld.set_debug_node(self.__debug_np.node())

    def stop(self): self.__debug_np.remove_node()

    def ray_test_all(self, pt_a, pt_b, mask=None):
        args = [pt_a.vec, pt_b.vec, mask] if mask else [pt_a.vec, pt_b.vec]
        return self.wld.ray_test_all(*args)

    def do_physics(self, delta_t, num_substeps, size_substeps):
        return self.wld.do_physics(delta_t, num_substeps, size_substeps)

    def get_contacts(self, node):
        contacts = self.wld.contact_test(node).get_contacts()
        return [BulletContact(contact) for contact in contacts]

    def toggle_debug(self):
        hidden = self.__debug_np.is_hidden()
        (self.__debug_np.show if hidden else self.__debug_np.hide)()


class BulletContact(object):

    def __init__(self, contact):
        self.contact = contact

    @property
    def node0(self): return self.contact.get_node0()

    @property
    def node1(self): return self.contact.get_node1()


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
