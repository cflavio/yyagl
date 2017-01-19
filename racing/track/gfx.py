from panda3d.core import AmbientLight, BitMask32, Spotlight, NodePath,\
    OmniBoundingVolume, Camera, OrthographicLens, TextureStage
from direct.actor.Actor import Actor
from yyagl.gameobject import Gfx
from direct.gui.OnscreenText import OnscreenText
from random import shuffle


class TrackGfx(Gfx):

    def __init__(self, mdt, split_world, submodels):
        self.ambient_np = None
        self.spot_lgt = None
        self.model = None
        self.split_world = split_world
        self.submodels = submodels
        self.__actors = []
        self.__flat_roots = {}
        Gfx.__init__(self, mdt)
        self.__init_signs()

    def async_build(self):
        self.__set_model()
        self.__set_light()

    def __set_model(self):
        eng.log_mgr.log('loading track model')
        self.notify('on_loading', _('loading track model'))
        time = globalClock.getFrameTime()
        path = self.mdt.path + '/track'
        eng.gfx.load_model(path, callback=self.__set_submod, extraArgs=[time])

    def __set_submod(self, model, time):
        d_t = round(globalClock.getFrameTime() - time, 2)
        eng.log_mgr.log('loaded track model (%s seconds)' % str(d_t))
        self.model = model
        for submodel in self.model.getChildren():
            self.__flat_sm(submodel)
        self.model.hide(BitMask32.bit(0))
        (self.__load_empties if self.submodels else self.end_loading)()

    @staticmethod
    def __flat_sm(submodel):
        s_n = submodel.getName()
        if not s_n.startswith('Empty'):
            submodel.flattenLight()

    def __load_empties(self):
        eng.log_mgr.log('loading track submodels')
        empty_models = self.model.findAllMatches('**/Empty*')

        def load_models():
            self.__process_models(list(empty_models))
        names = [model.getName().split('.')[0][5:] for model in empty_models]
        self.__preload_models(list(set(list(names))), load_models)

    def __preload_models(self, models, callback, model='', time=0):
        curr_t = globalClock.getFrameTime()
        d_t = curr_t - time
        if model:
            eng.log_mgr.log('loaded model: %s (%s seconds)' % (model, d_t))
        if not models:
            callback()
            return
        model = models.pop(0)
        self.notify('on_loading', _('loading model: ') + model)
        path = self.mdt.path + '/' + model
        if model.endswith('Anim'):
            self.__actors += [Actor(path, {'anim': path + '-Anim'})]
            self.__preload_models(models, callback, model, curr_t)
        else:
            eng.base.loader.loadModel(path, callback=
                lambda model: self.__preload_models(models, callback, model, curr_t))

    def __process_models(self, models):
        for model in models:
            model_name = model.getName().split('.')[0][5:]
            if model_name.endswith('Anim'):
                path = self.mdt.path + '/' + model_name
                self.__actors += [Actor(path, {'anim': path + '-Anim'})]
                self.__actors[-1].loop('anim')
                self.__actors[-1].setPlayRate(.5, 'anim')
                self.__actors[-1].reparent_to(model)
                if model.has_tag('omni') and model.get_tag('omni'):
                    eng.log_mgr.log('set omni for ' + self.__actors[-1].get_name())
                    self.__actors[-1].node().setBounds(OmniBoundingVolume())
                    self.__actors[-1].node().setFinal(True)
            else:
                self.__process_static(model)
        self.flattening()

    def __process_static(self, model):
        model_name = model.getName().split('.')[0][5:]
        if model_name not in self.__flat_roots:
            nstr = lambda i: '%s_%s' % (model_name, str(i))
            flat_roots = [self.model.attachNewNode(nstr(i)) for i in range(4)]
            self.__flat_roots[model_name] = flat_roots
        path = self.mdt.path + '/' + model.getName().split('.')[0][5:]
        eng.base.loader.loadModel(path).reparent_to(model)
        left, right, top, bottom = self.mdt.phys.lrtb
        center_x, center_y = (left + right) / 2, (top + bottom) / 2
        pos_x, pos_y = model.get_pos()[0], model.get_pos()[1]
        if not game.options['development']['split_world']:
            model.reparentTo(self.__flat_roots[model_name][0])
        elif pos_x < center_x and pos_y < center_y:
            model.reparentTo(self.__flat_roots[model_name][0])
        elif pos_x >= center_x and pos_y < center_y:
            model.reparentTo(self.__flat_roots[model_name][1])
        elif pos_x < center_x and pos_y >= center_y:
            model.reparentTo(self.__flat_roots[model_name][2])
        else:
            model.reparentTo(self.__flat_roots[model_name][3])

    def flattening(self):
        eng.log_mgr.log('track flattening')
        self.__flat_models(eng.logic.flatlist(self.__flat_roots.values()))

    def __flat_models(self, models, model='', time=0, nodes=0):
        if model:
            str_tmpl = 'flattened model: %s (%s seconds, %s nodes)'
            d_t = round(globalClock.getFrameTime() - time, 2)
            eng.log_mgr.log(str_tmpl % (model, d_t, nodes))
        if models:
            self.__process_flat_models(models, self.end_loading)
        else:
            self.end_loading()

    def __process_flat_models(self, models, callback):
        curr_t = globalClock.getFrameTime()
        node = models[0]
        node.clearModelNodes()

        def process_flat(flatten_node, orig_node, model, time, nodes, remove=True):
            flatten_node.reparent_to(orig_node.get_parent())
            if remove: orig_node.remove_node()  # remove 1.9.3
            self.__flat_models(models[1:], model, time, nodes)
        nname = node.get_name()
        self.notify('on_loading', _('flattening model: ') + nname)
        if self.submodels:
            if not 'NameBillboard2' in nname:
                loader.asyncFlattenStrong(
                    node, callback=process_flat, inPlace=False,
                    extraArgs=[node, nname, curr_t, len(node.get_children())])
            else:
                process_flat(node, node, nname, curr_t, 0, False)
        else:
            len_children = len(node.get_children())
            process_flat(node, NodePath(''), node, curr_t, len_children)

    def end_loading(self):
        self.__set_signs()
        self.model.prepareScene(eng.base.win.getGsg())
        Gfx.async_build(self)

    def __set_light(self):
        if game.options['development']['shaders']:
            eng.shader_mgr.set_amb_lgt((.15, .15, .15, 1))
            eng.shader_mgr.set_dir_lgt((.8, .8, .8, 1), (-25, -65, 0))
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
        self.spot_lgt.setPos(50, -80, 80)
        self.spot_lgt.lookAt(0, 0, 0)
        render.setLight(self.spot_lgt)
        render.setShaderAuto()

    def __init_signs(self):
        self.buffers = []
        self.drs = []
        self.cameras = []
        self.renders = []

    def __set_signs(self):
        signs = self.model.findAllMatches('**/NameBillboard2.egg')
        names = open('assets/thanks.txt').readlines()
        for i, sign in enumerate(signs):
            self.__set_render_to_texture()
            shuffle(names)
            text = '\n\n'.join(names[:3])
            txt = OnscreenText(text, parent=self.renders[i], scale=.2, fg=(0, 0, 0, 1), pos=(-.2, -.28))
            while txt.getTightBounds()[1][0] - txt.getTightBounds()[0][0] > .8:
                txt.setScale(txt.getScale()[0] - .01, txt.getScale()[0] - .01)
            height = txt.getTightBounds()[1][2] - txt.getTightBounds()[0][2]
            txt.setZ(-.24 + height / 2)
            ts = TextureStage('ts')
            ts.setMode(TextureStage.MDecal)
            sign.setTexture(ts, self.buffers[i].getTexture())

    def __set_render_to_texture(self):
        self.buffers += [base.win.makeTextureBuffer('result buffer', 512, 512)]
        self.buffers[-1].setSort(-100)

        self.drs += [self.buffers[-1].makeDisplayRegion()]
        self.drs[-1].setSort(20)

        self.cameras += [NodePath(Camera('camera 2d'))]
        lens = OrthographicLens()
        lens.setFilmSize(1.2, 2)
        lens.setNearFar(-1000, 1000)
        self.cameras[-1].node().setLens(lens)

        self.renders += [NodePath('result render')]
        self.renders[-1].setDepthTest(False)
        self.renders[-1].setDepthWrite(False)
        self.cameras[-1].reparentTo(self.renders[-1])
        self.drs[-1].setCamera(self.cameras[-1])

    def __destroy_signs(self):
        map(lambda buf: buf.destroy(), self.buffers)
        map(lambda dr: dr.destroy(), self.drs)
        map(lambda cam: cam.destroy(), self.cameras)
        map(lambda ren: ren.destroy(), self.renders)

    def destroy(self):
        self.model.removeNode()
        if not game.options['development']['shaders']:
            eng.base.render.clearLight(self.ambient_np)
            eng.base.render.clearLight(self.spot_lgt)
            self.ambient_np.removeNode()
            self.spot_lgt.removeNode()
        else:
            eng.shader_mgr.clear_lights()
        self.__actors = self.__flat_roots = None
        self.__destroy_signs()
