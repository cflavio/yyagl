from yyagl.gameobject import Colleague
from yyagl.lib.bullet.bullet import (
    BulletPhysWorld, BulletTriangleMesh, BulletTriangleMeshShape,
    BulletRigidBodyNode, BulletGhostNode)


PhysWorld = BulletPhysWorld
TriangleMesh = BulletTriangleMesh
TriangleMeshShape = BulletTriangleMeshShape
RigidBodyNode = BulletRigidBodyNode
GhostNode = BulletGhostNode


class CollInfo(object):

    def __init__(self, node, time):
        self.node = node
        self.time = time


class PhysFacade:

    def attach_rigid_body(self, rbnode): return self.root.attach_rigid_body(rbnode)
    def remove_rigid_body(self, rbnode): return self.root.remove_rigid_body(rbnode)
    def attach_ghost(self, gnode): return self.root.attach_ghost(gnode)
    def remove_ghost(self, gnode): return self.root.remove_ghost(gnode)
    def attach_vehicle(self, vehicle): return self.root.attach_vehicle(vehicle)
    def remove_vehicle(self, vehicle): return self.root.remove_vehicle(vehicle)
    def ray_test_all(self, from_pos, to_pos, mask=None): return self.root.ray_test_all(from_pos, to_pos, mask)
    def ray_test_closest(self, from_pos, to_pos, mask=None): return self.root.ray_test_closest(from_pos, to_pos, mask)


class PhysMgr(Colleague, PhysFacade):

    def __init__(self, mediator):
        Colleague.__init__(self, mediator)
        self.collision_objs = []  # objects to be processed
        self.__obj2coll = {}  # {obj: [(node, coll_time), ...], ...}
        self.root = None
        self.__debug_np = None
        PhysFacade.__init__(self)

    def reset(self):
        self.collision_objs = []
        self.__obj2coll = {}
        self.root = PhysWorld()
        self.root.set_gravity((0, 0, -8.5))
        self.root.init_debug()

    def start(self):
        self.eng.attach_obs(self.on_frame, 2)

    def on_frame(self):
        self.root.do_phys(self.eng.lib.last_frame_dt, 10, 1/180.0)
        self.__do_collisions()

    def ray_test_closest(self, top, bottom):
        return self.root.ray_test_closest(top, bottom)

    def add_collision_obj(self, node): self.collision_objs += [node]

    def remove_collision_obj(self, node): self.collision_objs.remove(node)

    def stop(self):
        self.root.stop()
        self.root = None
        self.eng.detach_obs(self.on_frame)

    def __do_collisions(self):
        to_clear = self.collision_objs[:]
        # identical collisions are ignored for .25 seconds
        for obj in self.collision_objs:
            if obj not in self.__obj2coll: self.__obj2coll[obj] = []
            # for contact in self.root.get_contacts(obj):
            # this doesn't work in 1.9, the following works
            # odd, this doesn't work too
            # for contact in self.root.wld.contact_test(obj).get_contacts():
            result = self.root._wld.contact_test(obj)
            for contact in result.get_contacts():
                self.__process_contact(obj, contact.get_node0(), to_clear)
                self.__process_contact(obj, contact.get_node1(), to_clear)
        for obj in to_clear:
            if obj in self.__obj2coll:  # it may be that it isn't here e.g.
                # when you fire a rocket while you're very close to the prev
                # car and the rocket is removed suddenly
                for coll in self.__obj2coll[obj]:
                    if self.eng.curr_time - coll.time > .25:
                        self.__obj2coll[obj].remove(coll)

    def __process_contact(self, obj, node, to_clear):
        if node == obj: return
        if obj in to_clear: to_clear.remove(obj)
        if node in [coll.node for coll in self.__obj2coll[obj]]: return
        self.__obj2coll[obj] += [CollInfo(node, self.eng.curr_time)]
        self.eng.event.notify('on_collision', obj, node)

    def toggle_dbg(self):
        if self.root: self.root.toggle_dbg()
