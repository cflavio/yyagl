from panda3d.core import LineSegs, BitMask32, Point2, Point3
from yyagl.gameobject import PhysColleague, GameObject
from yyagl.racing.weapon.bonus.bonus import Bonus
from yyagl.engine.phys import TriangleMesh, TriangleMeshShape, GhostNode, \
    RigidBodyNode


class MeshBuilder(GameObject):

    def __init__(self, model, geom_names, is_ghost):
        GameObject.__init__(self)
        self.model = model
        self.rigid_bodies = []
        self.ghosts = []
        self.nodes = []
        map(lambda name: self.__set_mesh(name, is_ghost), geom_names)

    def __set_mesh(self, geom_name, is_ghost):
        self.eng.log_mgr.log('setting physics for: ' + geom_name)
        geoms = self.eng.lib.find_geoms(self.model, geom_name)
        if geoms: self._process_meshes(geoms, geom_name, is_ghost)

    def _build_mesh(self, geoms, geom_name, is_ghost, is_merged):
        mesh = TriangleMesh()
        name = self._add_geoms(geoms, mesh, geom_name)
        shape = TriangleMeshShape(mesh, dynamic=False)
        self._build(shape, name, is_ghost, is_merged)

    def _build(self, shape, geom_name, is_ghost, is_merged):
        if is_ghost:
            ncls = GhostNode
            meth = self.eng.phys_mgr.attach_ghost
            lst = self.ghosts
        else:
            ncls = RigidBodyNode
            meth = self.eng.phys_mgr.attach_rigid_body
            lst = self.rigid_bodies
        nodepath = self.eng.attach_node(ncls(geom_name).node)
        self.nodes += [nodepath]
        nodepath.add_shape(shape)
        meth(nodepath.get_node())
        lst += [nodepath.get_node()]
        nodepath.get_node().notify_collisions(True)
        if not is_merged:
            nodepath.set_collide_mask(BitMask32.bit(1) | BitMask32.bit(15))
        if is_ghost:
            nodepath.set_collide_mask(BitMask32.bit(16))

    def destroy(self):
        self.model = self.rigid_bodies = self.ghosts = self.nodes = None
        GameObject.destroy(self)


class MeshBuilderMerged(MeshBuilder):

    def _process_meshes(self, geoms, geom_name, is_ghost):
        self._build_mesh(geoms, geom_name, is_ghost, True)

    def _add_geoms(self, geoms, mesh, geom_name):
        for geom in geoms:
            for _geom in [g.decompose() for g in geom.node().get_geoms()]:
                mesh.add_geom(_geom, False,
                              geom.get_transform(self.model.node))
        return geom_name


class MeshBuilderUnmerged(MeshBuilder):

    def _process_meshes(self, geoms, geom_name, is_ghost):
        for geom in geoms:
            self._build_mesh(geom, geom_name, is_ghost, False)

    def _add_geoms(self, geoms, mesh, geom_name):
        for _geom in [g.decompose() for g in geoms.node().get_geoms()]:
            mesh.add_geom(_geom, False, geoms.get_transform(self.model.node))
        return geoms.get_name()


class TrackPhys(PhysColleague):

    def __init__(self, mediator, race_props):
        self.corners = self.model = self.wp2prevs = None
        self.bonuses = []
        self.rigid_bodies = []
        self.ghosts = []
        self.nodes = []
        self.generate_tsk = []
        self.race_props = race_props
        PhysColleague.__init__(self, mediator)

    def sync_bld(self):
        self.model = self.eng.load_model(self.race_props.track_coll_path)
        self.__set_meshes()
        self.__set_corners()
        self.__set_waypoints()
        self.__set_weapons()
        self.__hide_all_models()

    def __set_meshes(self):
        builders = [
            MeshBuilderUnmerged(self.model, self.race_props.unmerged_names, False),
            MeshBuilderMerged(self.model, self.race_props.merged_names, False),
            MeshBuilderMerged(self.model, self.race_props.ghost_names, True)]
        for bld in builders:
            self.nodes += bld.nodes
            self.ghosts += bld.ghosts
            self.rigid_bodies += bld.rigid_bodies
            bld.destroy()

    def __set_corners(self):
        corners = self.race_props.corner_names
        self.corners = [self.model.find('**/' + crn) for crn in corners]

    def __set_waypoints(self):
        wp_info = self.race_props.wp_info
        wp_root = self.model.find('**/' + wp_info.root_name)
        waypoints = wp_root.find_all_matches('**/%s*' % wp_info.wp_name)
        self.wp2prevs = {}
        for wayp in waypoints:
            wayp.set_python_tag('initial_pos', wayp.get_pos())
            # do a proper wp class
            wayp.set_python_tag('weapon_boxes', [])
            wpstr = '**/' + wp_info.wp_name
            prevs = wayp.get_tag(wp_info.prev_name).split(',')
            lst_wp = [wp_root.find(wpstr + idx) for idx in prevs]
            self.wp2prevs[wayp] = lst_wp

    def set_curr_wp(self, wayp): pass

    def __set_weapons(self):
        weapon_info = self.race_props.weapon_info
        weap_root = self.model.find('**/' + weapon_info.root_name)
        if not weap_root: return
        weapons = weap_root.find_all_matches('**/%s*' % weapon_info.weap_name)
        map(lambda weap: self.create_bonus(weap.get_pos()), weapons)

    def __hide_all_models(self):
        nms = self.race_props.unmerged_names + self.race_props.merged_names + \
            self.race_props.ghost_names
        map(self.__hide_models, nms)

    def __hide_models(self, name):
        models = self.model.find_all_matches('**/%s*' % name)
        map(lambda mod: mod.hide(), models)

    def get_start_pos_hpr(self, i):
        start_pos = (0, 0, 0)
        start_hpr = (0, 0, 0)
        node_str = '**/' + self.race_props.start_name + str(i + 1)
        start_node = self.model.find(node_str)
        if start_node:
            start_pos = start_node.get_pos()
            start_hpr = start_node.get_hpr()
        return start_pos, start_hpr

    @property
    def bounds(self):
        crn = self.corners
        return crn[0].x, crn[1].x, crn[0].y, crn[3].y

    def create_bonus(self, pos):
        self.eng.log('created bonus', True)
        prs = self.race_props
        bonus = Bonus(pos, prs.bonus_model, prs.bonus_suff, self, self.mediator.gfx)
        self.bonuses += [bonus]
        bonus.attach_obs(self.on_bonus_collected)

    def on_bonus_collected(self, bonus):
        bonus.detach_obs(self.on_bonus_collected)
        self.bonuses.remove(bonus)
        gen_tsk = self.eng.do_later(20, self.create_bonus, [bonus.pos])
        self.generate_tsk += [gen_tsk]
        self.eng.log('created task for bonus', True)

    def destroy(self):
        self.model = self.model.remove_node()
        map(lambda node: node.remove_node(), self.nodes)
        map(self.eng.phys_mgr.remove_rigid_body, self.rigid_bodies)
        map(self.eng.phys_mgr.remove_ghost, self.ghosts)
        map(lambda bon: bon.destroy(), self.bonuses)
        self.eng.log_tasks()
        map(self.eng.rm_do_later, self.generate_tsk)
        self.eng.log_tasks()
        self.corners = self.rigid_bodies = self.ghosts = self.nodes = \
            self.wp2prevs = self.generate_tsk = self.bonuses = None
        self.race_props = None
