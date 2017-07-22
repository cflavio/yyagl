from panda3d.bullet import BulletWorld, BulletDebugNode
from ..singleton import Singleton
from ..facade import Facade


class PhysFacade(Facade):

    def __init__(self):
        self._fwd_mth_lazy('attach_rigid_body', lambda: self.root.attachRigidBody)
        self._fwd_mth_lazy('remove_rigid_body', lambda: self.root.removeRigidBody)
        self._fwd_mth_lazy('attach_ghost', lambda: self.root.attachGhost)
        self._fwd_mth_lazy('remove_ghost', lambda: self.root.removeGhost)
        self._fwd_mth_lazy('attach_vehicle', lambda: self.root.attachVehicle)
        self._fwd_mth_lazy('remove_vehicle', lambda: self.root.removeVehicle)
        self._fwd_mth_lazy('ray_test_all', lambda: self.root.rayTestAll)

    def add_collision_obj(self, node):
        self.collision_objs += [node]

    def ray_test_closest(self, top, bottom, mask=None):
        if mask:
            return self.root.rayTestClosest(top, bottom, mask)
        else:
            return self.root.rayTestClosest(top, bottom)


class PhysMgr(PhysFacade):

    __metaclass__ = Singleton

    def __init__(self):
        self.collision_objs = []  # objects to be processed
        self.__obj2coll = {}  # obj: [(node, coll_time), ...]
        self.root = None
        self.__debug_np = None
        PhysFacade.__init__(self)

    def init(self):
        self.collision_objs = []
        self.__obj2coll = {}
        self.root = BulletWorld()
        self.root.setGravity((0, 0, -9.81))
        debug_node = BulletDebugNode('Debug')
        debug_node.show_bounding_boxes(True)
        self.__debug_np = render.attach_new_node(debug_node)
        self.root.set_debug_node(self.__debug_np.node())

    def start(self):
        eng.attach_obs(self.on_frame, 2)

    def on_frame(self):
        self.root.do_physics(globalClock.get_dt(), 10, 1/180.0)
        self.__do_collisions()

    def add_collision_obj(self, node):
        self.collision_objs += [node]

    def remove_collision_obj(self, node):
        self.collision_objs.remove(node)

    def stop(self):
        self.root = None
        self.__debug_np.removeNode()
        eng.detach_obs(self.on_frame)

    def __process_contact(self, obj, node, to_clear):
        if node == obj:
            return
        obj in to_clear and to_clear.remove(obj)
        if node in [coll[0] for coll in self.__obj2coll[obj]]:
            return
        self.__obj2coll[obj] += [(node, globalClock.get_frame_time())]
        eng.event.notify('on_collision', obj, node)

    def __do_collisions(self):
        to_clear = self.collision_objs[:]
        for obj in self.collision_objs:
            if obj not in self.__obj2coll:
                self.__obj2coll[obj] = []
            result = self.root.contact_test(obj)
            for contact in result.get_contacts():
                self.__process_contact(obj, contact.get_node0(), to_clear)
                self.__process_contact(obj, contact.get_node1(), to_clear)
        for obj in to_clear:
            if obj in self.__obj2coll:  # it may be that it isn't here e.g.
                # when you fire a rocket while you're very close to the prev
                # car and the rocket is removed suddenly
                for coll in self.__obj2coll[obj]:
                    if globalClock.get_frame_time() - coll[1] > .25:
                        self.__obj2coll[obj].remove(coll)

    def toggle_debug(self):
        is_hidden = self.__debug_np.is_hidden()
        (self.__debug_np.show if is_hidden else self.__debug_np.hide)()

    @staticmethod
    def find_geoms(model, name):
        # no need to be cached
        geoms = model.find_all_matches('**/+GeomNode')
        is_nm = lambda geom: geom.get_name().startswith(name)
        named_geoms = [geom for geom in geoms if is_nm(geom)]
        in_vec = [name in named_geom.get_name() for named_geom in named_geoms]
        indexes = [i for i, el in enumerate(in_vec) if el]
        return [named_geoms[i] for i in indexes]
