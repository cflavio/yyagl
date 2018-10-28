from yyagl.gameobject import Colleague
from yyagl.lib.bullet.bullet import BulletPhysWorld, BulletContact, \
    BulletTriangleMesh, BulletTriangleMeshShape, BulletRigidBodyNode, \
    BulletGhostNode
from ..facade import Facade


PhysWorld = BulletPhysWorld
Contact = BulletContact
TriangleMesh = BulletTriangleMesh
TriangleMeshShape = BulletTriangleMeshShape
RigidBodyNode = BulletRigidBodyNode
GhostNode = BulletGhostNode


class CollInfo(object):

    def __init__(self, node, time):
        self.node = node
        self.time = time


class PhysFacade(Facade):

    def __init__(self):
        fwd = self._fwd_mth
        fwd('attach_rigid_body', lambda obj: obj.root.attach_rigid_body)
        fwd('remove_rigid_body', lambda obj: obj.root.remove_rigid_body)
        fwd('attach_ghost', lambda obj: obj.root.attach_ghost)
        fwd('remove_ghost', lambda obj: obj.root.remove_ghost)
        fwd('attach_vehicle', lambda obj: obj.root.attach_vehicle)
        fwd('remove_vehicle', lambda obj: obj.root.remove_vehicle)
        fwd('ray_test_all', lambda obj: obj.root.ray_test_all)
        fwd('ray_test_closest', lambda obj: obj.root.ray_test_closest)


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
        self.root.do_physics(self.eng.lib.last_frame_dt(), 10, 1/180.0)
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
            result = self.root.wld.contact_test(obj)
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

    def toggle_debug(self):
        self.root.toggle_debug()
