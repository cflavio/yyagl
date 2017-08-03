from panda3d.bullet import BulletRigidBodyNode, BulletTriangleMesh, \
    BulletTriangleMeshShape, BulletGhostNode
from panda3d.core import LineSegs, BitMask32
from yyagl.gameobject import Phys
from yyagl.engine.log import LogMgr
from yyagl.engine.phys import PhysMgr
from yyagl.racing.weapon.bonus.bonus import Bonus


class TrackPhys(Phys):

    def __init__(
            self, mdt, race_props):
        self.corners = self.model = self.wp2prevs = self.wp_np = None
        self.bonuses = []
        self.rigid_bodies = []
        self.ghosts = []
        self.nodes = []
        self.generate_tsk = []
        self.rprops = race_props
        Phys.__init__(self, mdt)

    def sync_bld(self):
        self.model = loader.loadModel(self.rprops.coll_track_path)
        self.__set_meshes(self.rprops.unmerged, False, False)
        self.__set_meshes(self.rprops.merged, True, False)
        self.__set_meshes(self.rprops.ghosts, True, True)
        self.__set_corners()
        self.__set_waypoints()
        self.__set_weapons()
        self.__hide_models()

    def __set_meshes(self, geom_names, is_merged, is_ghost):
        # refactor using builder_merged, builder_ghost
        for geom_name in geom_names:
            self.__set_mesh(geom_name, is_merged, is_ghost)

    def __set_mesh(self, geom_name, is_merged, is_ghost):
        LogMgr().log('setting physics for: ' + geom_name)
        geoms = PhysMgr().find_geoms(self.model, geom_name)
        if geoms:
            self.__process_meshes(geoms, geom_name, is_merged, is_ghost)

    def __process_meshes(self, geoms, geom_name, merged, ghost):
        meth = self.add_geoms_merged if merged else self.add_geoms_unmerged
        if not merged:
            for geom in geoms:
                self.__build_mesh(meth, geom, geom_name, ghost, merged)
        else:
            self.__build_mesh(meth, geoms, geom_name, ghost, merged)

    def add_geoms_merged(self, geoms, mesh, geom_name):
        for geom in geoms:
            for _geom in [g.decompose() for g in geom.node().get_geoms()]:
                mesh.add_geom(_geom, False, geom.get_transform(self.model))
        return geom_name

    def add_geoms_unmerged(self, geoms, mesh, geom_name):
        for _geom in [g.decompose() for g in geoms.node().get_geoms()]:
            mesh.addGeom(_geom, False, geoms.get_transform(self.model))
        return geoms.get_name()

    def __build_mesh(self, meth, geoms, geom_name, ghost, merged):
        mesh = BulletTriangleMesh()
        name = meth(geoms, mesh, geom_name)
        shape = BulletTriangleMeshShape(mesh, dynamic=False)
        self.__build(shape, name, ghost, merged)

    def __build(self, shape, geom_name, ghost, merged):
        if ghost:
            ncls = BulletGhostNode
            meth = PhysMgr().attach_ghost
            lst = self.ghosts
        else:
            ncls = BulletRigidBodyNode
            meth = PhysMgr().attach_rigid_body
            lst = self.rigid_bodies
        nodepath = eng.attach_node(ncls(geom_name))
        self.nodes += [nodepath]
        nodepath.node().addShape(shape)
        meth(nodepath.node())
        lst += [nodepath.node()]
        nodepath.node().notify_collisions(True)
        if ghost or not merged:
            nodepath.set_collide_mask(BitMask32.bit(1))

    def __set_corners(self):
        corners = self.rprops.corner_names
        self.corners = [self.model.find('**/' + crn) for crn in corners]

    def __set_waypoints(self):
        wp_info = self.rprops.wp_info
        wp_root = self.model.find('**/' + wp_info.root_name)
        _waypoints = wp_root.find_all_matches('**/%s*' % wp_info.wp_name)
        self.wp2prevs = {}
        for w_p in _waypoints:
            w_p.set_python_tag('initial_pos', w_p.get_pos())
            # do a proper wp class
            w_p.set_python_tag('weapon_boxes', [])
            wpstr = '**/' + wp_info.wp_name
            prevs = w_p.getTag(wp_info.prev_name).split(',')
            lst_wp = [wp_root.find(wpstr + idx) for idx in prevs]
            self.wp2prevs[w_p] = lst_wp
        self.redraw_wps()

    def redraw_wps(self):
        # put draw in a decorator class
        if not self.rprops.show_waypoints or not self.wp2prevs:
            # it may be invoked on track's destruction
            return
        if self.wp_np:
            self.wp_np.remove_node()
        segs = LineSegs()
        for w_p in self.wp2prevs.keys():
            for dest in self.wp2prevs[w_p]:
                segs.moveTo(w_p.get_pos())
                segs.drawTo(dest.get_pos())
        segs_node = segs.create()
        self.wp_np = render.attach_new_node(segs_node)

    def __set_weapons(self):
        weapon_info = self.rprops.weapon_info
        weap_root = self.model.find('**/' + weapon_info.root_name)
        if not weap_root:
            return
        _weapons = weap_root.find_all_matches('**/%s*' % weapon_info.weap_name)
        for weap in _weapons:
            self.create_bonus(weap.get_pos())

    def __hide_models(self):
        nms = self.rprops.unmerged + self.rprops.merged + self.rprops.ghosts
        for mod in nms:
            models = self.model.find_all_matches('**/%s*' % mod)
            map(lambda mod: mod.hide(), models)

    def get_start_pos(self, i):
        start_pos = (0, 0, 0)
        start_pos_hpr = (0, 0, 0)
        node_str = '**/' + self.rprops.start + str(i + 1)
        start_pos_node = self.model.find(node_str)
        if start_pos_node:
            start_pos = start_pos_node.get_pos()
            start_pos_hpr = start_pos_node.get_hpr()
        return start_pos, start_pos_hpr

    @property
    def lrtb(self):
        return self.corners[0].getX(), self.corners[1].getX(), \
            self.corners[0].getY(), self.corners[3].getY()

    def create_bonus(self, pos):
        prs = self.rprops
        self.bonuses += [Bonus(pos, prs.bonus_model, prs.bonus_suff, self)]
        self.bonuses[-1].attach_obs(self.on_bonus_collected)

    def on_bonus_collected(self, bonus):
        bonus.detach_obs(self.on_bonus_collected)
        self.bonuses.remove(bonus)
        self.generate_tsk += [eng.do_later(20, self.create_bonus, [bonus.pos])]

    def destroy(self):
        self.model = self.model.remove_node()
        map(lambda chl: chl.remove_node(), self.nodes)
        map(PhysMgr().remove_rigid_body, self.rigid_bodies)
        map(PhysMgr().remove_ghost, self.ghosts)
        map(lambda bon: bon.destroy(), self.bonuses)
        map(eng.remove_do_later, self.generate_tsk)
        self.corners = self.rigid_bodies = self.ghosts = self.nodes = \
            self.wp2prevs = self.generate_tsk = self.bonuses = None
        if self.rprops.show_waypoints:  # in the drawing class
            self.wp_np = self.wp_np.remove_node()
        self.rprops = None
