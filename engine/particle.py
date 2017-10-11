from ..gameobject import GameObject
from yyagl.library.panda.particle import PandaParticle
LibParticle = PandaParticle


class Particle(GameObject):

    def __init__(self, parent, pos, hpr, color, tot_time):
        GameObject.__init__(self)
        self.__np = LibParticle.set_nodepath(parent, pos, hpr)
        LibParticle.set_shader(self.__np, color, tot_time)
        self.__destroy_tsk = self.eng.do_later(tot_time, self.destroy)

    def destroy(self):
        self.__destroy_tsk = self.eng.remove_do_later(self.__destroy_tsk)
        self.__np = self.__np.remove_node()
        GameObject.destroy(self)
