from os.path import exists
from panda3d.core import get_model_path, LightRampAttrib, PandaNode, NodePath, \
    AntialiasAttrib
from direct.particles.ParticleEffect import ParticleEffect
from direct.filter.CommonFilters import CommonFilters
from ..gameobject import Gfx


class EngineGfx(Gfx):

    def __init__(self, mdt, model_path, antialiasing):
        Gfx.__init__(self, mdt)
        get_model_path().append_directory(model_path)
        if base.appRunner:
            root_dir = base.appRunner.p3dFilename.get_dirname()
            get_model_path().append_directory(root_dir + '/' + model_path)
            get_model_path().append_directory(root_dir)
        mdt.base.enableParticles()
        render.set_shader_auto()
        render.set_two_sided(True)
        if antialiasing:
            render.set_antialias(AntialiasAttrib.MAuto)
        self.root = None

    def init(self):
        self.root = render.attachNewNode('world')

    def clean(self):
        self.root.removeNode()

    @staticmethod
    def load_model(*args, **kwargs):
        if exists(args[0] + '.bam'):
            args[0] += '.bam'
        return loader.loadModel(*args, **kwargs)

    @staticmethod
    def __set_toon():
        tempnode = NodePath(PandaNode('temp node'))
        tempnode.setAttrib(LightRampAttrib.make_single_threshold(.5, .4))
        tempnode.set_shader_auto()
        base.cam.node().set_initial_state(tempnode.get_state())
        CommonFilters(base.win, base.cam).set_cartoon_ink(separation=1)

    def print_stats(self):
        print '\n\n#####\nrender2d.analyze()'
        self.mdt.base.render2d.analyze()
        print '\n\n#####\nrender.analyze()'
        self.mdt.base.render.analyze()
        print '\n\n#####\nrender2d.ls()'
        self.mdt.base.render2d.ls()
        print '\n\n#####\nrender.ls()'
        self.mdt.base.render.ls()

    @staticmethod
    def particle(path, parent, render_parent, pos, timeout):
        par = ParticleEffect()
        par.loadConfig(path)
        par.start(parent=parent, renderParent=render_parent)
        par.set_pos(pos)
        args = timeout, lambda par: par.cleanup(), [par]
        eng.do_later(*args)
