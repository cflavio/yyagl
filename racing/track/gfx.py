from os.path import exists
from os import system
from panda3d.core import AmbientLight, BitMask32, Spotlight, NodePath, \
    OmniBoundingVolume
from direct.actor.Actor import Actor
from yyagl.gameobject import Gfx
from yyagl.engine.log import LogMgr
from .signs import Signs


class TrackGfx(Gfx):

    def __init__(
            self, mdt, trackgfx_props):
        self.ambient_np = None
        self.spot_lgt = None
        self.model = None
        self.empty_models = self.signs = None
        self.loaders = []
        self.__actors = []
        self.__flat_roots = {}
        self.props = trackgfx_props
        Gfx.__init__(self, mdt)

    def async_bld(self):
        self.__set_model()
        self.__set_light()

    def __set_model(self):
        LogMgr().log('loading track model')
        filename = 'assets/models/tracks/' + self.props.name + '/track_all.bam'
        if not exists(filename):
            system('python yyagl/build/process_track.py ' + self.props.name)
        LogMgr().log('loading ' + filename)
        eng.load_model(filename, callback=self.end_loading)

    def end_loading(self, model=None):
        if model:
            self.model = model
        anim_name = '**/%s*%s*' % (self.props.empty_name, self.props.anim_name)
        for model in self.model.findAllMatches(anim_name):
            # bam files don't contain actor info
            new_root = NodePath(model.get_name())
            new_root.reparent_to(model.get_parent())
            new_root.set_pos(model.get_pos())
            new_root.set_hpr(model.get_hpr())
            new_root.set_scale(model.get_scale())
            model_subname = model.get_name()[len(self.props.empty_name):]
            path = '%s/%s' % (self.props.track_path, model_subname)
            if '.' in path:
                path = path.split('.')[0]
            anim_path = '%s-%s' % (path, self.props.anim_name)
            self.__actors += [Actor(path, {'anim': anim_path})]
            self.__actors[-1].loop('anim')
            self.__actors[-1].setPlayRate(.5, 'anim')
            self.__actors[-1].reparent_to(new_root)
            has_omni = model.has_tag(self.props.omni_tag)
            if has_omni and model.get_tag(self.props.omni_tag):
                new_root.set_tag(self.props.omni_tag, 'True')
                a_n = self.__actors[-1].get_name()
                LogMgr().log('set omni for ' + a_n)
                self.__actors[-1].node().setBounds(OmniBoundingVolume())
                self.__actors[-1].node().setFinal(True)
            model.remove_node()
        self.signs = Signs(self.model, self.props.sign_name,
                           self.props.sign_cb)
        self.signs.set_signs()
        self.model.prepareScene(eng.base.win.getGsg())
        self.model.premungeScene(eng.base.win.getGsg())
        Gfx.async_bld(self)

    def __set_light(self):
        if self.props.shaders:
            eng.set_amb_lgt((.15, .15, .15, 1))
            eng.set_dir_lgt((.8, .8, .8, 1), (-25, -65, 0))
            return
        ambient_lgt = AmbientLight('ambient light')
        ambient_lgt.setColor((.7, .7, .55, 1))
        self.ambient_np = render.attachNewNode(ambient_lgt)
        render.setLight(self.ambient_np)

        self.spot_lgt = render.attachNewNode(Spotlight('Spot'))
        self.spot_lgt.node().setScene(render)
        self.spot_lgt.node().setShadowCaster(True, 1024, 1024)
        self.spot_lgt.node().getLens().setFov(40)
        self.spot_lgt.node().getLens().setNearFar(20, 200)
        self.spot_lgt.node().setCameraMask(BitMask32.bit(0))
        self.spot_lgt.setPos(*self.props.shadow_src)
        self.spot_lgt.lookAt(0, 0, 0)
        render.setLight(self.spot_lgt)
        render.setShaderAuto()

    def destroy(self):
        self.model.removeNode()
        if not self.props.shaders:
            render.clearLight(self.ambient_np)
            render.clearLight(self.spot_lgt)
            self.ambient_np.removeNode()
            self.spot_lgt.removeNode()
        else:
            eng.clear_lights()
        self.__actors = self.__flat_roots = None
        self.signs.destroy()
        self.empty_models = None
        map(loader.cancelRequest, self.loaders)
