from panda3d.core import loadPrcFileData, BitMask32, NodePath
loadPrcFileData('', 'window-type none')
loadPrcFileData('', 'audio-library-name null')
loadPrcFileData('', 'default-model-extension .bam')
import sys
import os
sys.path.append(os.getcwd())
from os import walk
from os.path import getsize
from direct.actor.Actor import Actor
from yyagl.engine.engine import Engine
from yyagl.gameobject import GameObject
from yyagl.build.mtprocesser import MultithreadedProcesser
from yracing.bitmasks import BitMasks


class Props:

    def __init__(self):
        self.track_dir = sys.argv[1]
        self.cores = int(sys.argv[2]) if len(sys.argv) >= 3 else 0
        self.model_name = 'track'
        self.empty_name = 'Empty'
        self.anim_name = 'Anim'


class GuiCfg:

    def __init__(self):
        self.antialiasing = False
        self.shaders = False
        self.volume = 1
        self.fixed_fps = 0


class ProfilingCfg:

    def __init__(self):
        self.pyprof_percall = False


class LangCfg:

    def __init__(self):
        self.lang = 'en'
        self.lang_domain = 'yorg'
        self.lang_path = 'assets/locale'


class DevCfg:

    def __init__(self, model_path='assets/models', shaders_dev=False,
                 pbr=False, gamma=1.0, menu_joypad=True):
        self.model_path = ''
        self.shaders_dev = shaders_dev
        self.pbr = pbr
        self.gamma = gamma
        self.menu_joypad = menu_joypad
        self.xmpp_server = ''
        self.port = 9099
        self.server = ''
        self.srgb = False


class Conf:

    def __init__(self):
        self.gui_cfg = GuiCfg()
        self.profiling_cfg = ProfilingCfg()
        self.lang_cfg = LangCfg()
        self.dev_cfg = DevCfg()


if __name__ == '__main__':
    eng = Engine(Conf())


class LegacyTrackProcesser(GameObject):

    def __init__(self):
        GameObject.__init__(self)
        self.__actors = []
        self._flat_roots = {}
        self.models_to_load = self.loading_models = None
        self.props = Props()
        fpath = self.props.track_dir + '/models/' + self.props.model_name
        self.__egg2bams()
        print('loading ' + fpath)
        self.model = self.eng.load_model(fpath)
        print('loaded ' + fpath)
        self._set_submodels()

    def __egg2bams(self):
        # troot = 'assets/tracks/'
        mp_mgr = MultithreadedProcesser(self.props.cores)
        cmds = []
        for root, _, filenames in walk(self.props.track_dir):
            for filename in filenames:
                fname = root + '/' + filename
                if fname.endswith('.egg'):
                    cmd_args = fname, fname[:-3] + 'bam'
                    cmds += [('egg2bam -txo -mipmap -ctex %s -o %s' %
                              cmd_args, getsize(fname))]
                    print('added command ' + cmds[-1][0])
        cmds = reversed(sorted(cmds, key=lambda pair: pair[1]))
        list(map(mp_mgr.add, [cmd[0] for cmd in cmds]))
        mp_mgr.run()

    def _set_submodels(self):
        print('loaded track model')
        for submodel in self.model.children:
            if not submodel.get_name().startswith(self.props.empty_name):
                submodel.flatten_light()
        self.model.hide(BitMask32.bit(BitMasks.general))
        self._load_empties()

    def _load_empties(self):
        print('loading track submodels')
        empty_name = '**/%s*' % self.props.empty_name
        e_m = self.model.find_all_matches(empty_name)
        load_models = lambda: self._process_models(list(e_m))
        names = [model.name.split('.')[0][5:] for model in e_m]
        self._preload_models(list(set(list(names))), load_models)

    def _preload_models(self, models, callback, model='', time=0):
        curr_t = self.eng.curr_time
        if model:
            print('loaded model: %s (%s seconds)' % (model, curr_t - time))
        if not models:
            callback()
            return
        model = models.pop(0)
        fpath = self.props.track_dir + '/models/' + model
        if model.endswith(self.props.anim_name):
            anim_path = '%s-%s' % (fpath, self.props.anim_name)
            self.__actors += [Actor(fpath, {'anim': anim_path})]
        else:
            model = loader.loadModel(fpath)
        self._preload_models(models, callback, model, curr_t)

    def _process_models(self, models):
        for model in models:
            model_name = self._get_model_name(model)
            if not model_name.endswith(self.props.anim_name):
                self._process_static(model)
        self.flattening()

    def _get_model_name(self, model):
        return model.name.split('.')[0][len(self.props.empty_name):]

    def _process_static(self, model):
        model_name = self._get_model_name(model)
        if model_name not in self._flat_roots:
            flat_root = self.model.attach_node(model_name)
            self._flat_roots[model_name] = flat_root
        fpath = '%s/models/%s' % (self.props.track_dir, model_name)
        self.eng.load_model(fpath).reparent_to(model)
        model.reparent_to(self._flat_roots[model_name])

    def flattening(self):
        flat_cores = 1  # max(1, multiprocessing.cpu_count() / 2)
        print('track flattening using %s cores' % flat_cores)
        self.loading_models = []
        self.models_to_load = list(self._flat_roots.values())
        [self.__flat_models() for _ in range(flat_cores)]

    def __flat_models(self, model='', time=0, nodes=0):
        if model:
            msg_tmpl = 'flattened model: %s (%s seconds, %s nodes)'
            self.loading_models.remove(model)
            d_t = round(self.eng.curr_time - time, 2)
            print(msg_tmpl % (model, d_t, nodes))
        if self.models_to_load:
            self.__process_flat_models(self.models_to_load.pop())
        elif not self.loading_models:
            self.end_flattening()

    def __process_flat_models(self, model):
        new_model = NodePath(model.name)
        new_model.reparent_to(model.parent)
        for child in model.node.get_children():
            nodepath = NodePath('newroot')
            nodepath.set_pos(child.get_pos())
            nodepath.set_hpr(child.get_hpr())
            nodepath.set_scale(child.get_scale())
            nodepath.reparent_to(new_model)
            for _child in child.get_children():
                for __child in _child.get_children():
                    __child.reparent_to(nodepath)
        new_model.clear_model_nodes()
        new_model.flatten_strong()
        name = model.name
        model.remove_node()
        self.loading_models += [name]
        curr_t = self.eng.curr_time
        self.__flat_models(name, curr_t, len(new_model.get_children()))

    def end_flattening(self):
        print('writing track_all.bam')
        fpath = self.props.track_dir + \
            '/models/track_all.bam'
        self.model.write_bam_file(fpath)


class TrackProcesser(LegacyTrackProcesser):

    def _set_submodels(self):
        print('loaded track model')
        for submodel in self.model.children:
            if not submodel.get_name().startswith(self.props.empty_name) and \
                    not submodel.get_name().startswith('Instanced') and not \
                    submodel.get_name().startswith('Empties'):
                submodel.flatten_light()
        self.model.hide(BitMask32.bit(BitMasks.general))
        self._load_empties()

    @staticmethod
    def _get_model_name(model): return model.parent.get_tag('path')

    @staticmethod
    def __get_path(model): return model.parent.get_tag('path') + '.egg'

    def _load_empties(self):
        print('loading track submodels')
        empty_name = '**/%s*' % self.props.empty_name
        e_m = self.model.find_all_matches(empty_name)
        load_models = lambda: self._process_models(list(e_m))
        names = [self.__get_path(model) for model in e_m]
        self._preload_models(list(set(list(names))), load_models)


if __name__ == '__main__':
    legacy_tracks = ['dubai', 'moon', 'nagano', 'orlando', 'rome', 'sheffield',
                     'toronto']
    track_name = sys.argv[1].split('/')[-1]
    cls = LegacyTrackProcesser if track_name in legacy_tracks else \
         TrackProcesser
    cls()
