from panda3d.bullet import (BulletWorld as BWorld,
    BulletDebugNode as BDebugNode,
    BulletTriangleMesh as BTriangleMesh,
    BulletTriangleMeshShape as BTriangleMeshShape,
    BulletRigidBodyNode as BRigidBodyNode,
    BulletGhostNode as BGhostNode)
from yyagl.facade import Facade


class BulletPhysWorld(Facade):

    def __init__(self):
        self._wld = BWorld()
        self.__debug_np = None
        mth_lst = [
            ('attach_rigid_body', lambda obj: obj._wld.attach_rigid_body),
            ('remove_rigid_body', lambda obj: obj._wld.remove_rigid_body),
            ('attach_ghost', lambda obj: obj._wld.attach_ghost),
            ('remove_ghost', lambda obj: obj._wld.remove_ghost),
            ('attach_vehicle', lambda obj: obj._wld.attach_vehicle),
            ('remove_vehicle', lambda obj: obj._wld.remove_vehicle),
            ('ray_test_closest', lambda obj: obj._wld.ray_test_closest),
            ('do_phys', lambda obj: obj._wld.do_physics)]
        Facade.__init__(self, mth_lst=mth_lst)

    def set_gravity(self, vec): return self._wld.set_gravity(vec)

    def init_debug(self):
        debug_node = BDebugNode('Debug')
        debug_node.show_bounding_boxes(True)
        self.__debug_np = render.attach_new_node(debug_node)
        self._wld.set_debug_node(self.__debug_np.node())

    def stop(self): self.__debug_np.remove_node()

    def ray_test_all(self, pt_a, pt_b, mask=None):
        args = [pt_a._vec, pt_b._vec, mask] if mask else [pt_a._vec, pt_b._vec]
        return self._wld.ray_test_all(*args)

    def toggle_dbg(self):
        hidden = self.__debug_np.is_hidden()
        (self.__debug_np.show if hidden else self.__debug_np.hide)()


class BulletTriangleMesh(object):

    def __init__(self):
        self._mesh = BTriangleMesh()

    def add_geom(self, geom, rm_dupl, xform):
        return self._mesh.add_geom(geom, rm_dupl, xform)


class BulletTriangleMeshShape(object):

    def __init__(self, mesh, dynamic):
        self._mesh_shape = BTriangleMeshShape(mesh._mesh, dynamic=dynamic)


class BulletRigidBodyNode(object):

    def __init__(self, name): self._node = BRigidBodyNode(name)


class BulletGhostNode(object):

    def __init__(self, name): self._node = BGhostNode(name)
