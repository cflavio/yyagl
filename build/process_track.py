from panda3d.core import loadPrcFileData, BitMask32
loadPrcFileData('', 'window-type none')
loadPrcFileData('', 'audio-library-name null')
loadPrcFileData('', 'default-model-extension .bam')
import sys
import os
sys.path.append(os.getcwd())
from os import walk, system
from yyagl.engine.engine import Engine
from direct.actor.Actor import Actor


class Props(object):

    def __init__(self):
        self.track_dir = sys.argv[1]
        self.model_name = 'track'
        self.empty_name = 'Empty'
        self.anim_name = 'Anim'
        self.track_name = sys.argv[1]


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
        self.models_to_load = self.empty_models = self.in_loading = None
        self.props = Props()
        fpath = self.props.track_dir + '/' + self.props.model_name
        self.preprocess()
        self.model = eng.load_model(fpath)
        self.__set_submodels()

    def preprocess(self):
        troot = 'assets/models/tracks/'
        for root, _, filenames in walk(troot + self.props.track_dir):
            for filename in filenames:
                fname = root + '/' + filename
                if fname.endswith('.egg'):
                    cmd_args = (fname, fname[:-3] + 'bam')
                    system('egg2bam -txo -mipmap -ctex %s -o %s' % cmd_args)

    def __set_submodels(self):
        print 'loaded track model'
        for submodel in self.model.getChildren():
            if not submodel.getName().startswith(self.props.empty_name):
                submodel.flatten_light()
        self.model.hide(BitMask32.bit(0))
        self.__load_empties()

    def __load_empties(self):
        print 'loading track submodels'
        empty_name = '**/%s*' % self.props.empty_name
        self.empty_models = self.model.find_all_matches(empty_name)

        def load_models():
            self.__process_models(list(self.empty_models))
        e_m = self.empty_models
        names = [model.get_name().split('.')[0][5:] for model in e_m]
        self.__preload_models(list(set(list(names))), load_models)

    def __preload_models(self, models, callback, model='', time=0):
        curr_t = globalClock.getFrameTime()
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
            self.__preload_models(models, callback, model, curr_t)
        else:
            fmod = loader.loadModel(fpath)
            self.__preload_models(models, callback, fmod, curr_t)

    def __process_models(self, models):
        empty_name = self.props.empty_name
        for model in models:
            model_name = model.get_name().split('.')[0][len(empty_name):]
            if not model_name.endswith(self.props.anim_name):
                self.__process_static(model)
        self.flattening()

    def __process_static(self, model):
        empty_name = self.props.empty_name
        model_name = model.get_name().split('.')[0][len(empty_name):]
        if model_name not in self.__flat_roots:
            flat_root = self.model.attach_new_node(model_name)
            self.__flat_roots[model_name] = flat_root
        model_subname = model.get_name().split('.')[0][len(empty_name):]
        fpath = '%s/%s' % (self.props.track_dir, model_subname)
        loader.loadModel(fpath).reparent_to(model)
        model.reparent_to(self.__flat_roots[model_name])

    def flattening(self):
        print 'track flattening'
        flat_cores = 1  # max(1, multiprocessing.cpu_count() / 2)
        print 'flattening using %s cores' % flat_cores
        self.in_loading = []
        self.models_to_load = self.__flat_roots.values()
        [self.__flat_models() for _ in range(flat_cores)]

    def __flat_models(self, model='', time=0, nodes=0):
        if model:
            msg_tmpl = 'flattened model: %s (%s seconds, %s nodes)'
            self.in_loading.remove(model)
            d_t = round(globalClock.getFrameTime() - time, 2)
            print msg_tmpl % (model, d_t, nodes)
        if self.models_to_load:
            mod = self.models_to_load.pop()
            self.__process_flat_models(mod)
        elif not self.in_loading:
            self.end_flattening()

    def __process_flat_models(self, mod):
        curr_t = globalClock.getFrameTime()
        node = mod
        node.clear_model_nodes()

        def process_flat(model, time, nodes):
            self.__flat_models(model, time, nodes)
        self.in_loading += [node.get_name()]
        node.flattenStrong()
        process_flat(node.get_name(), curr_t, len(node.get_children()))

    def end_flattening(self):
        print 'writing track_all.bam'
        fpath = 'assets/models/tracks/' + self.props.track_dir + \
            '/track_all.bam'
        self.model.write_bam_file(fpath)


TrackProcesser()
