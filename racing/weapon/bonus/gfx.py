from yyagl.gameobject import Gfx
from direct.actor.Actor import Actor


class BonusGfx(Gfx):

    def __init__(self, mdt, pos):
        self.model = None
        self.pos = pos
        Gfx.__init__(self, mdt)

    def sync_build(self):
        path = 'assets/models/weapons/bonus/WeaponboxAnim'
        self.model = Actor(path, {'anim': path + '-Anim'})
        self.model.reparent_to(render)
        self.model.set_pos(self.pos)
        self.model.loop('anim')
        self.model.setPlayRate(.5, 'anim')

    def destroy(self):
        self.model.remove_node()
        self.model = None
        Gfx.destroy(self)
