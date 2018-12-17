from os.path import exists
from os import system, makedirs
from sys import executable
from panda3d.core import NodePath, LPoint3f, LineSegs, BitMask32, Filename
from direct.gui.OnscreenText import OnscreenText
from yyagl.engine.gfx import AnimNode, AmbientLight, Spotlight
from yyagl.gameobject import GfxColleague
from yyagl.racing.bitmasks import BitMasks
from yyagl.lib.p3d.p3d import LibP3d
from .signs import Signs


class TrackGfx(GfxColleague):

    def __init__(self, mediator, race_props):
        self.ambient_np = self.spot_lgt = self.model = self.empty_models = \
            self.signs = self.ambient = None
        self.__anim_nodes = []
        self.__flat_roots = {}
        self.props = race_props
        self.props.track_dir = 'assets/models/tracks/%s/' % self.props.track_name
        GfxColleague.__init__(self, mediator)

    def async_bld(self):
        self.__set_meshes()
        self._set_light()

    def __set_meshes(self):
        self.eng.log_mgr.log('loading track model')
        if not exists(LibP3d.fixpath(self.__flattened_path)):
            #script_path = executable + ' yyagl/build/process_track.py'
            #system(script_path + ' ' + self.props.track_name)
            self.eng.do_later(.8, self.__launch_flattening)
        else: self.actual_load()

    def actual_load(self):
        self.eng.log_mgr.log('loading ' + self.__flattened_path)
        self.eng.gfx.gfx_mgr.load_model(self.__flattened_path, callback=self.end_loading)

    def __launch_flattening(self):
        self.model = self.eng.load_model('assets/models/tracks/%s/track' % self.props.track_name)
        self.__set_submodels()
        self.model.remove_node()
        self.actual_load()

    def end_loading(self, model):
        self.model = model
        rpr = self.props
        anim_name = '**/%s*%s*' % (rpr.empty_name, rpr.anim_name)
        for model in self.model.find_all_matches(anim_name):
            # bam files don't contain actor info
            cloned_root = self.__cloned_root(model)
            model_subname = model.name[len(rpr.empty_name):]
            # filenames are like EmptyModelName
            path = '%s/%s' % (rpr.track_path, model_subname)
            if '.' in path: path = path.split('.')[0]
            # e.g. desert/Model.001 (Blender appends that)
            self.__set_anim_node(path, cloned_root, model)
            model.remove_node()
        roots = self.model.find_all_matches('**/%s*' % rpr.sign_name)
        self.signs = Signs(roots, rpr.sign_cb)
        self.signs.set_signs()
        self.model.optimize()
        GfxColleague.async_bld(self)

    @staticmethod
    def __cloned_root(model):
        cloned_root = NodePath(model.name)
        cloned_root.reparent_to(model.parent)
        cloned_root.set_pos(model.get_pos())
        cloned_root.set_hpr(model.hpr)
        cloned_root.set_scale(model.scale)
        return cloned_root

    def __set_anim_node(self, path, cloned_root, model):
        anim_path = '%s-%s' % (path, self.props.anim_name)
        self.__anim_nodes += [AnimNode(path, {'anim': anim_path})]
        self.__anim_nodes[-1].loop('anim')
        self.__anim_nodes[-1].reparent_to(cloned_root)
        has_omni = model.has_tag(self.props.omni_tag)
        if has_omni and model.get_tag(self.props.omni_tag):
            self.__set_omni(cloned_root)

    def __set_omni(self, root):
        root.set_tag(self.props.omni_tag, 'True')
        a_n = self.__anim_nodes[-1].name
        self.eng.log_mgr.log('set omni for ' + a_n)
        self.__anim_nodes[-1].set_omni()

    def _set_light(self):
        self.ambient = AmbientLight((.7, .7, .55, 1))
        self.spot_lgt = Spotlight(BitMask32.bit(BitMasks.general))
        self.spot_lgt.set_pos(self.props.shadow_src)
        self.spot_lgt.look_at((0, 0, 0))
        if not self.props.shaders:
            self.spot_lgt.set_color((.2, .2, .2))
        sha = self.eng.gfx.gfx_mgr.shader_support and self.props.shaders
        if sha: self.eng.gfx.gfx_mgr.enable_shader()
        else: self.eng.gfx.gfx_mgr.disable_shader()

    def _destroy_lights(self):
        self.ambient.destroy()
        self.spot_lgt.destroy()

    def update(self, car_pos):
        sh_src = LPoint3f(*self.props.shadow_src)
        self.spot_lgt.set_pos(car_pos + sh_src)

    def redraw_wps(self): pass

    def __set_submodels(self):
        print 'loaded track model'
        for submodel in self.model.children:
            if not submodel.get_name().startswith(self.props.empty_name):
                submodel.flatten_light()
        self.model.hide(BitMask32.bit(BitMasks.general))
        self.__load_empties()

    def __load_empties(self):
        print 'loading track submodels'
        empty_name = '**/%s*' % self.props.empty_name
        e_m = self.model.find_all_matches(empty_name)
        load_models = lambda: self.__process_models(list(e_m))
        names = [model.name.split('.')[0][5:] for model in e_m]
        #self.__preload_models(list(set(list(names))), load_models)
        load_models()

    def __preload_models(self, models, callback, model='', time=0):
        curr_t = self.eng.curr_time
        if model:
            print 'loaded model: %s (%s seconds)' % (model, curr_t - time)
        if not models:
            callback()
            return
        model = models.pop(0)
        fpath = self.props.track_dir + '/' + model
        if model.endswith(self.props.anim_name):
            anim_path = '%s-%s' % (fpath, self.props.anim_name)
            self.__actors += [Actor(fpath, {'anim': anim_path})]
        else:
            model = loader.loadModel(fpath)
        self.__preload_models(models, callback, model, curr_t)

    def __process_models(self, models):
        for model in models:
            model_name = self.__get_model_name(model)
            if not model_name.endswith(self.props.anim_name):
                self.__process_static(model)
        self.flattening()

    def __get_model_name(self, model):
        return model.name.split('.')[0][len(self.props.empty_name):]

    def __process_static(self, model):
        model_name = self.__get_model_name(model)
        if model_name not in self.__flat_roots:
            flat_root = self.model.attach_node(model_name)
            self.__flat_roots[model_name] = flat_root
        fpath = '%s/%s' % (self.props.track_dir, model_name)
        self.eng.load_model(fpath).reparent_to(model)
        model.reparent_to(self.__flat_roots[model_name])

    def flattening(self):
        flat_cores = 1  # max(1, multiprocessing.cpu_count() / 2)
        print 'track flattening using %s cores' % flat_cores
        self.loading_models = []
        self.models_to_load = self.__flat_roots.values()
        [self.__flat_models() for _ in range(flat_cores)]

    def __flat_models(self, model='', time=0, nodes=0):
        if model:
            msg_tmpl = 'flattened model: %s (%s seconds, %s nodes)'
            self.loading_models.remove(model)
            d_t = round(self.eng.curr_time - time, 2)
            print msg_tmpl % (model, d_t, nodes)
        if self.models_to_load:
            self.__process_flat_models(self.models_to_load.pop())
        elif not self.loading_models:
            self.end_flattening()

    def __process_flat_models(self, model):
        new_model = NodePath(model.name)
        new_model.reparent_to(model.parent)
        for child in model.node.get_children():
            np = NodePath('newroot')
            np.set_pos(child.get_pos())
            np.set_hpr(child.get_hpr())
            np.set_scale(child.get_scale())
            np.reparent_to(new_model)
            for _child in child.get_children():
                for __child in _child.get_children():
                    __child.reparent_to(np)
        new_model.clear_model_nodes()
        new_model.flatten_strong()
        name = model.name
        model.remove_node()
        self.loading_models += [name]
        curr_t = self.eng.curr_time
        self.__flat_models(name, curr_t, len(new_model.get_children()))

    @property
    def __flattened_path(self):
        pre_path = str(Filename.get_user_appdata_directory()) + '/Yorg/' + self.props.track_dir
        #tracks_path = LibP3d.fixpath(pre_path)
        #return LibP3d.fixpath(tracks_path + 'track_all.bam')
        return pre_path + 'track_all.bam'

    def end_flattening(self):
        pre_path = str(Filename.get_user_appdata_directory()) + '/Yorg/' + self.props.track_dir
        tracks_path = LibP3d.fixpath(pre_path)
        if not exists(tracks_path): makedirs(str(Filename(tracks_path)))
        print 'writing ' + self.__flattened_path
        self.model.write_bam_file(self.__flattened_path)

    def destroy(self):
        map(lambda node: node.destroy(), self.__anim_nodes)
        self.model.remove_node()
        self._destroy_lights()
        self.__anim_nodes = self.__flat_roots = None
        self.signs.destroy()
        self.empty_models = None


class TrackGfxDebug(TrackGfx):

    def __init__(self, mediator, race_props):
        TrackGfx.__init__(self, mediator, race_props)
        self.curr_wp = ''
        self.wp_np = None
        self.wp2txt = {}
        self.eng.attach_obs(self.on_frame)
        self.eng.do_later(2.0, self.redraw_wps)

    def set_curr_wp(self, wayp):
        self.curr_wp = wayp.get_name()[8:]

    def on_frame(self):
        if hasattr(self.mediator, 'phys') and not self.wp2txt:
            for wayp in self.mediator.phys.waypoints:
                self.wp2txt[wayp] = OnscreenText(wayp.get_name()[8:],
                                                 fg=(1, 1, 1, 1), scale=.08)
        if not hasattr(self.mediator, 'phys'): return  # first frame, refactor
        map(self.__process_wp, self.mediator.phys.waypoints)

    def __process_wp(self, wayp):
        pos2d = self.eng.gfx.gfx_mgr.pos2d(wayp.node)
        if pos2d:
            self.wp2txt[wayp].show()
            self.wp2txt[wayp].setPos(1.7777 * pos2d[0] + .02,
                                     pos2d[1] + .02)
            # refactor: set_pos doesn't work
            self.wp2txt[wayp]['fg'] = (1, 0, 0, 1) if \
                wayp.get_name()[8:] == self.curr_wp else (1, 1, 1, 1)
        else: self.wp2txt[wayp].hide()

    def redraw_wps(self):
        if not hasattr(self.mediator, 'phys'): return  # first frame, refactor
        if not self.mediator.phys.waypoints: return
        # it may be invoked on track's destruction
        if self.wp_np: self.wp_np.remove_node()
        segs = LineSegs()
        for w_p in self.mediator.phys.waypoints:
            for dest in w_p.prevs:
                segs.moveTo(w_p.pos)
                segs.drawTo(dest.pos)
        segs_node = segs.create()
        self.wp_np = render.attach_new_node(segs_node)

    def destroy(self):
        self.eng.detach_obs(self.on_frame)
        if self.wp_np: self.wp_np = self.wp_np.remove_node()
        map(lambda txt: txt.destroy(), self.wp2txt.values())
        self.wp2txt = self.mediator.phys.waypoints = None
        TrackGfx.destroy(self)


class TrackGfxShader(TrackGfx):

    def update(self, car_pos): pass

    def _set_light(self):
        self.eng.set_amb_lgt((.15, .15, .15, 1))
        self.eng.set_dir_lgt((.8, .8, .8, 1), (-25, -65, 0))

    def _destroy_lights(self): self.eng.clear_lights()
