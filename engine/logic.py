from urllib import urlopen
from os.path import exists
from ..gameobject import LogicColleague
from .configuration import Cfg
from yyagl.gameobject import GameObject
from yyagl.computer_proxy import ComputerProxy, compute_once


class VersionChecker(GameObject, ComputerProxy):

    def __init__(self):
        GameObject.__init__(self)
        ComputerProxy.__init__(self)

    @compute_once
    def is_uptodate(self):
        try:
            ver = urlopen('http://ya2.it/yorg_version.txt').read()
        except IOError:
            return False
        major, minor, build = ver.split('.')
        major, minor, build = int(major), int(minor), int(build)
        curr_ver = self.eng.version
        if curr_ver == 'deploy-ng': return True
        curr_major, curr_minor, curr_build = curr_ver.split('-')[0].split('.')
        curr_major = int(curr_major)
        curr_minor = int(curr_minor)
        curr_build = int(curr_build)
        return curr_major > major or \
            curr_major == major and curr_minor > minor or \
            curr_major == major and curr_minor == minor and curr_build >= build

    def destroy(self):
        GameObject.destroy(self)
        # ComputerProxy.destroy(self)  # raises an exception


class EngineLogic(LogicColleague):

    def __init__(self, mediator, cfg=None):
        LogicColleague.__init__(self, mediator)
        self.cfg = cfg or Cfg()  # use a default conf if not provided

    @property
    def version(self):
        if not self.is_runtime:
            if not exists('assets/version.txt'): return '-'
            with open('assets/version.txt') as fver:
                return fver.read().strip() + '-source'
        return self.mediator.lib.build_version

    @property
    def is_runtime(self):
        return self.mediator.lib.runtime

    @property
    def curr_path(self):
        return self.mediator.lib.curr_path + '/' \
            if self.is_runtime else ''

    def destroy(self):
        self.cfg = None
        LogicColleague.destroy(self)
