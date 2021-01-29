# from math import pi
# from ..gameobject import GameObject
from yyagl.lib.p3d.particle import P3dParticle
Particle = P3dParticle


# class Particle(GameObject):

#    def __init__(self, emitter, texture, npart, color=(1, 1, 1, 1), ampl=pi/6,
#                 ray=.5, rate=.0001, gravity=-.85, vel=3.8, part_lifetime=1.0,
#                 autodestroy=None):
#        if not self.eng.lib.version.startswith('1.10'): return
#        GameObject.__init__(self)
#        LibParticle(
#            emitter, texture, npart, color, ampl, ray, rate, gravity, vel,
#            part_lifetime, autodestroy)
