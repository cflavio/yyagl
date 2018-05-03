from panda3d.core import LineSegs, BitMask32, Point2, Point3
from yyagl.computer_proxy import ComputerProxy, compute_once, once_a_frame
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


class Waypoint(object):

    def __init__(self, node):
        self.node = node
        self.initial_pos = node.get_pos()
        self.weapon_boxes = []
        self.prevs = []
        self.prevs_grid = []
        self.__grid_wps = {}

    def set_prevs(self, waypoints, prev_name, wp_root, wpstr):
        prevs = self.node.get_tag(prev_name).split(',')
        prev_nodes =  [wp_root.find(wpstr + idx) for idx in prevs]
        def find_wp(name):
            for wayp in waypoints:
                if wayp.name == name: return wayp
        prev_names = [wayp.get_name() for wayp in prev_nodes]
        self.prevs = [find_wp(name) for name in prev_names]

    def set_prevs_grid(self, nopitlane_wps):
        self.prevs_grid = [wayp for wayp in self.prevs if wayp in nopitlane_wps]

    @property
    def name(self): return self.node.get_name()

    @property
    def pos(self): return self.node.get_pos()

    def __repr__(self):
        prevs = [wp.name[8:] for wp in self.prevs]
        prevs_grid = [wp.name[8:] for wp in self.prevs_grid]
        prevs_nogrid = [wp.name[8:] for wp in self.prevs_nogrid]
        prevs_nopitlane = [wp.name[8:] for wp in self.prevs_nopitlane]
        return self.name[8:] + ' [%s]' % ','.join(prevs) + \
            ' [%s]' % ','.join(prevs_grid) + \
            ' [%s]' % ','.join(prevs_nogrid) + \
            ' [%s]' % ','.join(prevs_nopitlane)


class TrackPhys(PhysColleague, ComputerProxy):

    def __init__(self, mediator, race_props):
        ComputerProxy.__init__(self)
        self.corners = self.model = None
        self.bonuses = []
        self.rigid_bodies = []
        self.ghosts = []
        self.nodes = []
        self.generate_tsk = []
        self.waypoints = []
        self.race_props = race_props
        self.__grid_wps = {}
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
        for wayp in waypoints:
            wpstr = '**/' + wp_info.wp_name
            neww = Waypoint(wayp)
            self.waypoints += [neww]
        for wayp in self.waypoints:
            wayp.set_prevs(self.waypoints, wp_info.prev_name, wp_root, wpstr)
        for wayp in self.waypoints:
            # it uses the results of the previous step: can't use the same for
            wayp.set_prevs_grid(self.nopitlane_wps(wayp))
        for w_p in self.waypoints:
            w_p.prevs_nogrid = self.nogrid_wps(w_p)
        for w_p in self.waypoints:
            w_p.prevs_nopitlane = self.nopitlane_wps(w_p)
        if self.eng.cfg.dev_cfg.verbose:
            import pprint
            to_print = [self.waypoints, self.pitstop_wps, self.grid_wps]
            map(pprint.pprint, to_print)

    def nopitlane_wps(self, curr_wp):
        if curr_wp in self.__grid_wps:
            return self.__grid_wps[curr_wp]
        wps = self.waypoints[:]
        if curr_wp not in self.pitstop_wps:
            for _wp in self.pitstop_wps:
                wps.remove(_wp)
        self.__grid_wps[curr_wp] = wps
        return wps

    @compute_once
    def nogrid_wps(self, curr_wp):
        wps = self.waypoints[:]
        if curr_wp not in self.grid_wps:
            for _wp in self.grid_wps:
                wps.remove(_wp)
        return wps

    @property
    def grid_wps(self):
        wps = self.waypoints
        start_forks = [w_p for w_p in wps if len(w_p.prevs) > 1]

        def parents(w_p):
            return [pwp for pwp in wps if w_p in pwp.prevs]
        end_forks = [w_p for w_p in wps if len(parents(w_p)) > 1]
        grid_forks = []
        for w_p in start_forks:
            for start in w_p.prevs[:]:
                to_process = [start]
                is_grid = False
                is_pitstop = False
                try_forks = []
                while to_process:
                    next_wp = to_process.pop(0)
                    try_forks += [next_wp]
                    for nwp in next_wp.prevs:
                        if nwp not in end_forks:
                            to_process += [nwp]
                        if 'Goal' in self.__get_hits(next_wp, nwp):
                            is_grid = True
                        if 'PitStop' in self.__get_hits(next_wp, nwp):
                            is_pitstop = True
                if is_grid and not is_pitstop:
                    grid_forks += try_forks
        return grid_forks

    @property
    def pitstop_wps(self):
        # it returns the waypoints of the pitlane
        wps = self.waypoints
        start_forks = [w_p for w_p in wps if len(w_p.prevs) > 1]

        def parents(w_p):
            return [pwp for pwp in wps if w_p in pwp.prevs]
        end_forks = [w_p for w_p in wps if len(parents(w_p)) > 1]
        pitstop_forks = []
        for w_p in start_forks:
            for start in w_p.prevs[:]:
                to_process = [start]
                is_pit_stop = False
                try_forks = []
                while to_process:
                    next_wp = to_process.pop(0)
                    try_forks += [next_wp]
                    for nwp in next_wp.prevs:
                        if nwp not in end_forks:
                            to_process += [nwp]
                        if 'PitStop' in self.__get_hits(next_wp, nwp):
                            is_pit_stop = True
                if is_pit_stop:
                    pitstop_forks += try_forks
        return pitstop_forks

    @staticmethod
    def __get_hits(wp1, wp2):
        return [
            hit.get_node().get_name()
            for hit in TrackPhys.eng.phys_mgr.ray_test_all(
                wp1.pos, wp2.pos).get_hits()]

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
            self.generate_tsk = self.bonuses = self.race_props = \
            self.waypoints = None
        ComputerProxy.destroy(self)
