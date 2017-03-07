from panda3d.bullet import BulletRigidBodyNode, BulletTriangleMesh, \
    BulletTriangleMeshShape, BulletGhostNode
from yyagl.gameobject import Phys
from yyagl.racing.weapon.bonus.bonus import Bonus
from panda3d.core import LineSegs


class TrackPhys(Phys):

    def __init__(
            self, mdt, path, unmerged, merged, ghosts, corner_names,
            waypoint_names, show_waypoints, weapons, weapon_names, start):
        self.corners = None
        self.bonuses = []
        self.rigid_bodies = []
        self.ghosts = []
        self.nodes = []
        self.path = path
        self.unmerged = unmerged
        self.merged = merged
        self.ghost_names = ghosts
        self.corner_names = corner_names
        self.waypoint_names = waypoint_names
        self.show_waypoints = show_waypoints
        self.weapons = weapons
        self.weapon_names = weapon_names
        self.start = start
        Phys.__init__(self, mdt)

    def sync_build(self):
        self.model = loader.loadModel(self.path)
        self.__load(self.unmerged, False, False)
        self.__load(self.merged, True, False)
        self.__load(self.ghost_names, True, True)
        self.__set_corners()
        self.__set_waypoints()
        self.__set_weapons()
        self.__hide_models()

    def __load(self, names, merged, ghost):
        for geom_name in names:
            eng.log_mgr.log('setting physics for: ' + geom_name)
            geoms = eng.phys.find_geoms(self.model, geom_name)  # facade
            if geoms:
                self.__process_meshes(geoms, geom_name, merged, ghost)

    def __process_meshes(self, geoms, geom_name, merged, ghost):
        meth = self.add_geoms_merged if merged else self.add_geoms_unmerged
        if not merged:
            for geom in geoms:
                self.__build_mesh(meth, geom, geom_name, ghost)
        else:
            self.__build_mesh(meth, geoms, geom_name, ghost)

    def add_geoms_merged(self, geoms, mesh, geom_name):
        for geom in geoms:
            geom.flattenLight()
            for _geom in [g.decompose() for g in geom.node().getGeoms()]:
                mesh.addGeom(_geom, geom.getTransform(self.model))
        return geom_name

    def add_geoms_unmerged(self, geoms, mesh, geom_name):
        geoms.flattenLight()
        for _geom in [g.decompose() for g in geoms.node().getGeoms()]:
            mesh.addGeom(_geom, geoms.getTransform(self.model))
        return geoms.get_name()

    def __build_mesh(self, meth, geoms, geom_name, ghost):
        mesh = BulletTriangleMesh()
        name = meth(geoms, mesh, geom_name)
        shape = BulletTriangleMeshShape(mesh, dynamic=False)
        self.__build(shape, name, ghost)

    def __build(self, shape, geom_name, ghost):
        if ghost:
            ncls = BulletGhostNode
            meth = eng.phys.world_phys.attachGhost  # facade
            lst = self.ghosts
        else:
            ncls = BulletRigidBodyNode
            meth = eng.phys.world_phys.attachRigidBody  # facade
            lst = self.rigid_bodies
        nodepath = eng.gfx.world_np.attachNewNode(ncls(geom_name))  # facade
        self.nodes += [nodepath]
        nodepath.node().addShape(shape)
        meth(nodepath.node())
        lst += [nodepath.node()]
        nodepath.node().notifyCollisions(True)

    def __set_corners(self):
        pmod = self.model
        self.corners = [pmod.find('**/' + crn) for crn in self.corner_names]

    def __set_waypoints(self):
        wp_root = self.model.find('**/' + self.waypoint_names[0])
        _waypoints = wp_root.findAllMatches('**/%s*' % self.waypoint_names[1])
        self.waypoints = {}
        for w_p in _waypoints:
            wpstr = '**/' + self.waypoint_names[1]
            prevs = w_p.getTag(self.waypoint_names[2]).split(',')
            lst_wp = [wp_root.find(wpstr + idx) for idx in prevs]
            self.waypoints[w_p] = lst_wp
        if not self.show_waypoints:
            return
        segs = LineSegs()
        for w_p in self.waypoints.keys():
            for dest in self.waypoints[w_p]:
                segs.moveTo(w_p.get_pos())
                segs.drawTo(dest.get_pos())
        segs_node = segs.create()
        self.wp_np = render.attachNewNode(segs_node)

    def create_bonus(self, pos):
        self.bonuses += [Bonus(pos)]

    def __set_weapons(self):
        if not self.weapons:
            return
        weap_root = self.model.find('**/' + self.weapon_names[0])
        if not weap_root:
            return
        _weapons = weap_root.findAllMatches('**/%s*' % self.weapon_names[1])
        for weap in _weapons:
            self.create_bonus(weap.get_pos())

    def __hide_models(self):
        for mod in self.unmerged + self.merged + self.ghost_names:
            models = self.model.findAllMatches('**/%s*' % mod)
            map(lambda mod: mod.hide(), models)

    def get_start_pos(self, i):
        start_pos = (0, 0, 0)
        start_pos_hpr = (0, 0, 0)
        node_str = '**/' + self.start + str(i + 1)
        start_pos_node = self.model.find(node_str)
        if start_pos_node:
            start_pos = start_pos_node.get_pos()
            start_pos_hpr = start_pos_node.get_hpr()
        return start_pos, start_pos_hpr

    @property
    def lrtb(self):
        return self.corners[0].getX(), self.corners[1].getX(), \
            self.corners[0].getY(), self.corners[3].getY()

    def destroy(self):
        self.model.removeNode()
        map(lambda chl: chl.remove_node(), self.nodes)
        map(eng.phys.world_phys.remove_rigid_body, self.rigid_bodies)  # facade
        map(eng.phys.world_phys.remove_ghost, self.ghosts)  # facade
        self.corners = self.rigid_bodies = self.ghosts = self.nodes = \
            self.waypoints = None
        map(lambda bon: bon.destroy(), self.bonuses)
        if not self.show_waypoints:
            return
        self.wp_np.remove_node()
