from ..gameobject import GameObject
from yyagl.lib.p3d.particle import P3dParticle
LibParticle = P3dParticle


class Particle(GameObject):

    def __init__(self, parent, pos, hpr, color, tot_time):
        if not self.eng.lib.version.startswith('1.10'): return
        GameObject.__init__(self)
        self.__part = LibParticle(parent, pos, hpr, color, tot_time)
        self.__destroy_tsk = self.eng.do_later(tot_time, self.destroy)

    def destroy(self):
        if not self.eng.lib.version.startswith('1.10'): return
        self.__destroy_tsk = self.eng.rm_do_later(self.__destroy_tsk)
        self.__part = self.__part.destroy()
        GameObject.destroy(self)
