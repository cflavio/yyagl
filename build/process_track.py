from panda3d.core import loadPrcFileData, BitMask32
loadPrcFileData('', 'window-type none')
loadPrcFileData('', 'audio-library-name null')
import sys
import os
sys.path.append(os.getcwd())
from yyagl.engine.engine import Engine
from direct.actor.Actor import Actor


class Props(object):

    def __init__(self):
        self.path = sys.argv[1]
        self.model_name = 'track'
        self.empty_name = 'Empty'
        self.anim_name = 'Anim'
        self.name = sys.argv[1]


class Conf(object):

    def __init__(self):
        self.model_path = 'assets/models/tracks/'
        self.antialiasing = False
        self.menu_joypad = False
        self.shaders = False
        self.gamma = 1.0
        self.lang = 'en'
        self.lang_domain = 'yorg'
        self.lang_path = 'assets/locale'
        self.volume = 1


eng = Engine(Conf())


class TrackProcesser(object):

    def __init__(self):
        self.__actors = []
        self.__flat_roots = {}
        self.props = Props()
        path = self.props.path + '/' + self.props.model_name
        self.model = eng.load_model(path)
        self.__set_submod()

    def __set_submod(self):
        print 'loaded track model'
        for submodel in self.model.getChildren():
            self.__flat_sm(submodel)
        self.model.hide(BitMask32.bit(0))
        self.__load_empties()

    def __flat_sm(self, submodel):
        s_n = submodel.getName()
        if not s_n.startswith(self.props.empty_name):
            submodel.flattenLight()

    def __load_empties(self):
        print 'loading track submodels'
        empty_name = '**/%s*' % self.props.empty_name
        self.empty_models = self.model.findAllMatches(empty_name)

        def load_models():
            self.__process_models(list(self.empty_models))
        e_m = self.empty_models
        names = [model.getName().split('.')[0][5:] for model in e_m]
        self.__preload_models(list(set(list(names))), load_models)

    def __preload_models(self, models, callback, model='', time=0):
        curr_t = globalClock.getFrameTime()
        d_t = curr_t - time
        if model:
            print 'loaded model: %s (%s seconds)' % (model, d_t)
        if not models:
            callback()
            return
        model = models.pop(0)
        path = self.props.path + '/' + model
        if model.endswith(self.props.anim_name):
            anim_path = '%s-%s' % (path, self.props.anim_name)
            self.__actors += [Actor(path, {'anim': anim_path})]
            self.__preload_models(models, callback, model, curr_t)
        else:
            def p_l(model):
                self.__preload_models(models, callback, model, curr_t)
            p_l(loader.loadModel(path))

    def __process_models(self, models):
        empty_name = self.props.empty_name
        for model in models:
            model_name = model.getName().split('.')[0][len(empty_name):]
            if not model_name.endswith(self.props.anim_name):
                self.__process_static(model)
        self.flattening()

    def __process_static(self, model):
        empty_name = self.props.empty_name
        model_name = model.getName().split('.')[0][len(empty_name):]
        if model_name not in self.__flat_roots:
            flat_root = self.model.attachNewNode(model_name)
            self.__flat_roots[model_name] = flat_root
        model_subname = model.getName().split('.')[0][len(empty_name):]
        path = '%s/%s' % (self.props.path, model_subname)
        loader.loadModel(path).reparent_to(model)
        model.reparentTo(self.__flat_roots[model_name])

    def flattening(self):
        print 'track flattening'
        flat_cores = 1  # max(1, multiprocessing.cpu_count() / 2)
        print 'flattening using %s cores' % flat_cores
        self.in_loading = []
        self.models_to_load = self.__flat_roots.values()
        for i in range(flat_cores):
            self.__flat_models()

    def __flat_models(self, model='', time=0, nodes=0):
        if model:
            str_tmpl = 'flattened model: %s (%s seconds, %s nodes)'
            self.in_loading.remove(model)
            d_t = round(globalClock.getFrameTime() - time, 2)
            print str_tmpl % (model, d_t, nodes)
        if self.models_to_load:
            mod = self.models_to_load.pop()
            self.__process_flat_models(mod, self.end_flattening)
        elif not self.in_loading:
            self.end_flattening()

    def __process_flat_models(self, mod, callback):
        curr_t = globalClock.getFrameTime()
        node = mod
        node.clearModelNodes()

        def process_flat(model, time, nodes):
            self.__flat_models(model, time, nodes)
        nname = node.get_name()
        self.in_loading += [nname]
        node.flattenStrong()
        process_flat(nname, curr_t, len(node.get_children()))

    def end_flattening(self, model=None):
        print 'writing track.bam'
        self.model.writeBamFile('assets/models/tracks/' + self.props.path +
                                '/track.bam')


TrackProcesser()
