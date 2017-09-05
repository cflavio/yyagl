from panda3d.core import Mat4
from ..gameobject import Logic
from .configuration import Cfg


class EngineLogic(Logic):

    def __init__(self, mdt, cfg=None):
        Logic.__init__(self, mdt)
        self.cfg = cfg or Cfg()

    @property
    def version(self):
        if not self.eng.base.appRunner:
            with open('assets/version.txt') as fver:
                return fver.read().strip() + '-source'
        package = self.eng.base.appRunner.p3dInfo.FirstChildElement('package')
        return package.Attribute('version')

    @property
    def is_runtime(self):
        return base.appRunner

    @property
    def curr_path(self):
        return base.appRunner.p3dFilename.getDirname() + '/' \
            if self.is_runtime else ''

    @staticmethod
    def norm_vec(vec):
        vec.normalize()
        return vec

    @staticmethod
    def rot_vec(vec, deg):
        rot_mat = Mat4()
        rot_mat.setRotateMat(deg, (0, 0, 1))
        return rot_mat.xform_vec(vec)

    def destroy(self):
        self.cfg = None
        Logic.destroy(self)
