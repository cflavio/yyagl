from ..gameobject import Logic
from .configuration import Cfg


class EngineLogic(Logic):

    def __init__(self, mdt, cfg=None):
        Logic.__init__(self, mdt)
        self.cfg = cfg or Cfg()

    @property
    def version(self):
        if not eng.base.appRunner:
            return 'source'
        package = eng.base.appRunner.p3dInfo.FirstChildElement('package')
        return package.Attribute('version')

    @property
    def is_runtime(self):
        return base.appRunner

    @property
    def curr_path(self):
        return base.appRunner.p3dFilename.getDirname() + '/' \
            if self.is_runtime else ''

    def destroy(self):
        self.cfg = None
        Logic.destroy(self)
