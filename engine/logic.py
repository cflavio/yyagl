from ..gameobject import Logic
from .configuration import Configuration


class EngineLogic(Logic):

    def __init__(self, mdt, cfg=None):
        Logic.__init__(self, mdt)
        self.cfg = cfg or Configuration()

    @property
    def version(self):
        if not eng.base.appRunner:
            return 'source'
        package = eng.base.appRunner.p3dInfo.FirstChildElement('package')
        return package.Attribute('version')

    @staticmethod
    def flatlist(lst):
        return [item for sublist in lst for item in sublist]

    @property
    def is_runtime(self):
        return base.appRunner and base.appRunner.dom
