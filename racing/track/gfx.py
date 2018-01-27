from os.path import exists
from os import system
from sys import executable
from panda3d.core import AmbientLight, BitMask32, Spotlight, NodePath, \
    OmniBoundingVolume
from direct.actor.Actor import Actor
from yyagl.gameobject import GfxColleague
from .signs import Signs


class TrackGfx(GfxColleague):

    def __init__(self, mediator, race_props):
        self.ambient_np = self.spot_lgt = self.model = self.empty_models = \
            self.signs = None
        self.loaders = []
        self.__actors = []
        self.__flat_roots = {}
        self.rprops = race_props
        GfxColleague.__init__(self, mediator)

    def async_bld(self):
        self.__set_model()
        self._set_light()

    def __set_model(self):
        self.eng.log_mgr.log('loading track model')
        ftmpl = 'assets/models/tracks/%s/track_all.bam'
        filename = ftmpl % self.rprops.track_name
        if not exists(filename):
            script_path = executable + ' yyagl/build/process_track.py'
            system(script_path + ' ' + self.rprops.track_name)
        self.eng.log_mgr.log('loading ' + filename)
        self.eng.gfx.gfx_mgr.load_model(filename, callback=self.end_loading)

    def end_loading(self, model):
        self.model = model
        anim_name = '**/%s*%s*' % (self.rprops.empty_name,
                                   self.rprops.anim_name)
        for model in self.model.find_all_matches(anim_name):
            # bam files don't contain actor info
            cloned_root = NodePath(model.get_name())
            cloned_root.reparent_to(model.get_parent())
            cloned_root.set_pos(model.get_pos())
            cloned_root.set_hpr(model.get_hpr())
            cloned_root.set_scale(model.get_scale())
            model_subname = model.get_name()[len(self.rprops.empty_name):]
            # filenames are like EmptyModelName
            path = '%s/%s' % (self.rprops.track_path, model_subname)
            if '.' in path:
                path = path.split('.')[0]
                # e.g. desert/Model.001 (Blender appends that)
            anim_path = '%s-%s' % (path, self.rprops.anim_name)
            self.__actors += [Actor(path, {'anim': anim_path})]
            self.__actors[-1].loop('anim')
            self.__actors[-1].reparent_to(cloned_root)
            has_omni = model.has_tag(self.rprops.omni_tag)
            if has_omni and model.get_tag(self.rprops.omni_tag):
                self.__set_omni(cloned_root)
            model.remove_node()
        roots = self.model.find_all_matches('**/%s*' % self.rprops.sign_name)
        self.signs = Signs(roots, self.rprops.sign_cb)
        self.signs.set_signs()
        self.model.prepare_scene()
        self.model.premunge_scene()
        GfxColleague.async_bld(self)

    def __set_omni(self, root):
        root.set_tag(self.rprops.omni_tag, 'True')
        a_n = self.__actors[-1].get_name()
        self.eng.log_mgr.log('set omni for ' + a_n)
        self.__actors[-1].node().set_bounds(OmniBoundingVolume())
        self.__actors[-1].node().set_final(True)

    def _set_light(self):
        ambient_lgt = AmbientLight('ambient light')
        ambient_lgt.set_color((.7, .7, .55, 1))
        self.ambient_np = render.attach_new_node(ambient_lgt)
        render.set_light(self.ambient_np)

        self.spot_lgt = render.attach_new_node(Spotlight('Spot'))
        self.spot_lgt.node().set_scene(render)
        self.spot_lgt.node().set_shadow_caster(True, 1024, 1024)
        self.spot_lgt.node().get_lens().set_fov(40)
        self.spot_lgt.node().get_lens().set_near_far(20, 200)
        self.spot_lgt.node().set_camera_mask(BitMask32.bit(0))
        self.spot_lgt.set_pos(*self.rprops.shadow_src)
        self.spot_lgt.look_at(0, 0, 0)
        if not self.rprops.shaders:
            self.spot_lgt.set_color(.2, .2, .2)
        render.set_light(self.spot_lgt)
        shaders_supp = base.win.get_gsg().get_supports_basic_shaders()
        if shaders_supp and self.rprops.shaders:
            render.set_shader_auto()
        else:
            render.set_shader_off()

    def _destroy_lights(self):
        render.clear_light(self.ambient_np)
        render.clear_light(self.spot_lgt)
        self.ambient_np.remove_node()
        self.spot_lgt.remove_node()

    def destroy(self):
        map(lambda act: act.cleanup(), self.__actors)
        self.model.remove_node()
        self._destroy_lights()
        self.__actors = self.__flat_roots = None
        self.signs.destroy()
        self.empty_models = None
        map(loader.cancelRequest, self.loaders)


class TrackGfxShader(TrackGfx):

    def _set_light(self):
        self.eng.set_amb_lgt((.15, .15, .15, 1))
        self.eng.set_dir_lgt((.8, .8, .8, 1), (-25, -65, 0))

    def _destroy_lights(self):
        self.eng.clear_lights()
