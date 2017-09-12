from panda3d.core import loadPrcFileData, BitMask32
loadPrcFileData('', 'window-type none')
loadPrcFileData('', 'audio-library-name null')
loadPrcFileData('', 'default-model-extension .bam')
import sys
import os
sys.path.append(os.getcwd())
from os import walk, system
from yyagl.engine.engine import Engine
from yyagl.gameobject import GameObject
from direct.actor.Actor import Actor


class Props(object):

    def __init__(self):
        self.track_dir = sys.argv[1]
        self.model_name = 'track'
        self.empty_name = 'Empty'
        self.anim_name = 'Anim'


class Conf(object):

    def __init__(self):
        self.model_path = 'assets/models/tracks/'
        self.antialiasing = self.menu_joypad = self.shaders_dev = \
            self.py_profiling = self.py_profiling_percall = False
        self.gamma = 1.0
        self.lang = 'en'
        self.lang_domain = 'yorg'
        self.lang_path = 'assets/locale'
        self.volume = 1


eng = Engine(Conf())


class TrackProcesser(GameObject):

    def __init__(self):
        GameObject.__init__(self)
        self.__actors = []
        self.__flat_roots = {}
        self.models_to_load = self.loading_models = None
        self.props = Props()
        fpath = self.props.track_dir + '/' + self.props.model_name
        self.__egg2bams()
        self.model = self.eng.load_model(fpath)
        self.__set_submodels()

    def __egg2bams(self):
        troot = 'assets/models/tracks/'
        for root, _, filenames in walk(troot + self.props.track_dir):
            for filename in filenames:
                fname = root + '/' + filename
                if fname.endswith('.egg'):
                    cmd_args = fname, fname[:-3] + 'bam'
                    system('egg2bam -txo -mipmap -ctex %s -o %s' % cmd_args)

    def __set_submodels(self):
        print 'loaded track model'
        for submodel in self.model.getChildren():
            if not submodel.get_name().startswith(self.props.empty_name):
                submodel.flatten_light()
        self.model.hide(BitMask32.bit(0))
        self.__load_empties()

    def __load_empties(self):
        print 'loading track submodels'
        empty_name = '**/%s*' % self.props.empty_name
        e_m = self.model.find_all_matches(empty_name)
        load_models = lambda: self.__process_models(list(e_m))
        names = [model.get_name().split('.')[0][5:] for model in e_m]
        self.__preload_models(list(set(list(names))), load_models)

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
        return model.get_name().split('.')[0][len(self.props.empty_name):]

    def __process_static(self, model):
        model_name = self.__get_model_name(model)
        if model_name not in self.__flat_roots:
            flat_root = self.model.attach_new_node(model_name)
            self.__flat_roots[model_name] = flat_root
        fpath = '%s/%s' % (self.props.track_dir, model_name)
        loader.loadModel(fpath).reparent_to(model)
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
        model.clear_model_nodes()
        self.loading_models += [model.get_name()]
        model.flattenStrong()
        curr_t = self.eng.curr_time
        self.__flat_models(model.get_name(), curr_t, len(model.get_children()))

    def end_flattening(self):
        print 'writing track_all.bam'
        fpath = 'assets/models/tracks/' + self.props.track_dir + \
            '/track_all.bam'
        self.model.write_bam_file(fpath)


TrackProcesser()
