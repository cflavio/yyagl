from os.path import exists
from os import system
from sys import executable
from panda3d.core import BitMask32, NodePath, OmniBoundingVolume, LPoint3f
from yyagl.engine.gfx import AnimNode, AmbientLight, Spotlight
from yyagl.gameobject import GfxColleague
from .signs import Signs


class TrackGfx(GfxColleague):

    def __init__(self, mediator, race_props):
        self.ambient_np = self.spot_lgt = self.model = self.empty_models = \
            self.signs = None
        self.__anim_nodes = []
        self.__flat_roots = {}
        self.raceprops = race_props
        GfxColleague.__init__(self, mediator)

    def async_bld(self):
        self.__set_meshes()
        self._set_light()

    def __set_meshes(self):
        self.eng.log_mgr.log('loading track model')
        filename = self.raceprops.gfx_track_path
        if not exists(filename):
            script_path = executable + ' yyagl/build/process_track.py'
            system(script_path + ' ' + self.raceprops.track_name)
        self.eng.log_mgr.log('loading ' + filename)
        self.eng.gfx.gfx_mgr.load_model(filename, callback=self.end_loading)

    def end_loading(self, model):
        self.model = model
        rpr = self.raceprops
        anim_name = '**/%s*%s*' % (rpr.empty_name, rpr.anim_name)
        for model in self.model.find_all_matches(anim_name):
            # bam files don't contain actor info
            cloned_root = self.__cloned_root(model)
            model_subname = model.get_name()[len(rpr.empty_name):]
            # filenames are like EmptyModelName
            path = '%s/%s' % (rpr.track_path, model_subname)
            if '.' in path: path = path.split('.')[0]
            # e.g. desert/Model.001 (Blender appends that)
            self.__set_anim_node(path, cloned_root, model)
            model.remove_node()
        roots = self.model.find_all_matches('**/%s*' % rpr.sign_name)
        self.signs = Signs(roots, rpr.sign_cb)
        self.signs.set_signs()
        self.model.prepare_scene()
        self.model.premunge_scene()
        GfxColleague.async_bld(self)

    def __cloned_root(self, model):
        cloned_root = NodePath(model.get_name())
        cloned_root.reparent_to(model.get_parent())
        cloned_root.set_pos(model.get_pos())
        cloned_root.set_hpr(model.get_hpr())
        cloned_root.set_scale(model.get_scale())
        return cloned_root

    def __set_anim_node(self, path, cloned_root, model):
        anim_path = '%s-%s' % (path, self.raceprops.anim_name)
        self.__anim_nodes += [AnimNode(path, {'anim': anim_path})]
        self.__anim_nodes[-1].loop('anim')
        self.__anim_nodes[-1].reparent_to(cloned_root)
        has_omni = model.has_tag(self.raceprops.omni_tag)
        if has_omni and model.get_tag(self.raceprops.omni_tag):
            self.__set_omni(cloned_root)

    def __set_omni(self, root):
        root.set_tag(self.raceprops.omni_tag, 'True')
        a_n = self.__anim_nodes[-1].get_name()
        self.eng.log_mgr.log('set omni for ' + a_n)
        self.__anim_nodes[-1].set_omni()

    def _set_light(self):
        self.ambient = AmbientLight((.7, .7, .55, 1))
        self.spot_lgt = Spotlight()
        self.spot_lgt.set_pos(self.raceprops.shadow_src)
        self.spot_lgt.look_at((0, 0, 0))
        if not self.raceprops.shaders:
            self.spot_lgt.set_color((.2, .2, .2))
        sha = self.eng.gfx.gfx_mgr.shader_support and self.raceprops.shaders
        self.eng.gfx.gfx_mgr.set_shader(sha)

    def _destroy_lights(self):
        self.ambient.destroy()
        self.spot_lgt.destroy()

    def update(self, car_pos):
        sh_src = LPoint3f(*self.raceprops.shadow_src)
        self.spot_lgt.set_pos(car_pos + sh_src)

    def destroy(self):
        map(lambda node: node.destroy(), self.__anim_nodes)
        self.model.remove_node()
        self._destroy_lights()
        self.__anim_nodes = self.__flat_roots = None
        self.signs.destroy()
        self.empty_models = None


class TrackGfxShader(TrackGfx):

    def update(self, car_pos): pass

    def _set_light(self):
        self.eng.set_amb_lgt((.15, .15, .15, 1))
        self.eng.set_dir_lgt((.8, .8, .8, 1), (-25, -65, 0))

    def _destroy_lights(self): self.eng.clear_lights()
