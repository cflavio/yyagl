from panda3d.bullet import (BulletWorld as BWorld,
    BulletDebugNode as BDebugNode,
    BulletTriangleMesh as BTriangleMesh,
    BulletTriangleMeshShape as BTriangleMeshShape,
    BulletRigidBodyNode as BRigidBodyNode,
    BulletGhostNode as BGhostNode)


class BulletPhysWorld:

    def __init__(self):
        self._wld = BWorld()
        self.__debug_np = None

    def attach_rigid_body(self, rbnode): return self._wld.attach_rigid_body(rbnode)
    def remove_rigid_body(self, rbnode): return self._wld.remove_rigid_body(rbnode)
    def attach_ghost(self, gnode): return self._wld.attach_ghost(gnode)
    def remove_ghost(self, gnode): return self._wld.remove_ghost(gnode)
    def attach_vehicle(self, vehicle): return self._wld.attach_vehicle(vehicle)
    def remove_vehicle(self, vehicle): return self._wld.remove_vehicle(vehicle)
    def ray_test_closest(self, from_pos, to_pos, mask=None):
        if mask is not None: return self._wld.ray_test_closest(from_pos, to_pos, mask)
        else: return self._wld.ray_test_closest(from_pos, to_pos)
    def do_phys(self, dt, max_substeps, stepsize): return self._wld.do_physics(dt, max_substeps, stepsize)

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
