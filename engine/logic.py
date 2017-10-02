from os.path import exists
from panda3d.core import Mat4
from ..gameobject import Logic
from .configuration import Cfg


class EngineLogic(Logic):

    def __init__(self, mdt, cfg=None):
        Logic.__init__(self, mdt)
        self.cfg = cfg or Cfg()  # use a default conf if not provided

    @property
    def version(self):
        if not self.is_runtime:
            if not exists('assets/version.txt'): return '-'
            with open('assets/version.txt') as fver:
                return fver.read().strip() + '-source'
        return self.mdt.lib.build_version

    @property
    def is_runtime(self):
        return self.mdt.lib.runtime

    @property
    def curr_path(self):
        return self.mdt.lib.curr_path + '/' \
            if self.is_runtime else ''

    def destroy(self):
        self.cfg = None
        Logic.destroy(self)
