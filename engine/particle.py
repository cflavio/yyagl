from math import pi
from ..gameobject import GameObject
from yyagl.lib.p3d.particle import P3dParticle
LibParticle = P3dParticle


class Particle(GameObject):

    def __init__(self, emitter, texture, tot_time, npart, color=(1, 1, 1, 1), ampl=pi/6, ray=.5, rate=.0001, gravity=-.85, vel=3.8, part_time=None):
        if not self.eng.lib.version.startswith('1.10'): return
        GameObject.__init__(self)
        if part_time is None: part_time = tot_time
        self.__part = LibParticle(emitter, texture, part_time, npart, color,
                                  ampl, ray, rate, gravity, vel)
        self.__destroy_tsk = self.eng.do_later(tot_time, self.destroy)

    def destroy(self):
        if not self.eng.lib.version.startswith('1.10'): return
        self.__destroy_tsk = self.eng.rm_do_later(self.__destroy_tsk)
        self.__part = self.__part.destroy()
        GameObject.destroy(self)
