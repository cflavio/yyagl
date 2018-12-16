from panda3d.core import loadPrcFileData, BitMask32, NodePath
loadPrcFileData('', 'window-type none')
loadPrcFileData('', 'audio-library-name null')
loadPrcFileData('', 'default-model-extension .bam')
import sys
import os
sys.path.append(os.getcwd())
from os import walk, system
from os.path import getsize
from yyagl.engine.engine import Engine
from yyagl.gameobject import GameObject
from direct.actor.Actor import Actor
from yyagl.build.mtprocesser import MultithreadedProcesser
from yyagl.racing.bitmasks import BitMasks


class Props(object):

    def __init__(self):
        self.track_dir = sys.argv[1]
        self.cores = int(sys.argv[2]) if len(sys.argv) >= 3 else 0
        self.model_name = 'track'
        self.empty_name = 'Empty'
        self.anim_name = 'Anim'


class GuiCfg(object):

    def __init__(self):
        self.antialiasing = False
        self.shaders = False
        self.volume = 1


class ProfilingCfg(object):

    def __init__(self):
        self.pyprof_percall = False


class LangCfg(object):

    def __init__(self):
        self.lang = 'en'
        self.lang_domain = 'yorg'
        self.lang_path = 'assets/locale'


class DevCfg(object):

    def __init__(self, model_path='assets/models', shaders_dev=False,
                 gamma=1.0, menu_joypad=True):
        self.model_path = 'assets/models/tracks/'
        self.shaders_dev = False
        self.gamma = 1.0
        self.menu_joypad = False
        self.xmpp_server = ''
        self.port = 9099
        self.server = ''


class Conf(object):

    def __init__(self):
        self.gui_cfg = GuiCfg()
        self.profiling_cfg = ProfilingCfg()
        self.lang_cfg = LangCfg()
        self.dev_cfg = DevCfg()


eng = Engine(Conf())


class TrackProcesser(GameObject):

    def __init__(self):
        GameObject.__init__(self)
        self.__actors = []
        self.__flat_roots = {}
        self.models_to_load = self.loading_models = None
        self.props = Props()
        self.__egg2bams()

    def __egg2bams(self):
        troot = 'assets/models/tracks/'
        mp_mgr = MultithreadedProcesser(self.props.cores)
        cmds = []
        for root, _, filenames in walk(troot + self.props.track_dir):
            for filename in filenames:
                fname = root + '/' + filename
                if fname.endswith('.egg'):
                    cmd_args = fname, fname[:-3] + 'bam'
                    cmds += [('egg2bam -txo -mipmap -ctex %s -o %s' % cmd_args, getsize(fname))]
        cmds = reversed(sorted(cmds, key=lambda pair: pair[1]))
        map(mp_mgr.add, [cmd[0] for cmd in cmds])
        mp_mgr.run()


TrackProcesser()
