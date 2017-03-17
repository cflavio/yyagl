from direct.actor.Actor import Actor
from yyagl.gameobject import Gfx


class BonusGfx(Gfx):

    def __init__(self, mdt, pos, model_name, model_suff):
        self.model = None
        self.pos = pos
        self.model_name = model_name
        self.model_suff = model_suff
        Gfx.__init__(self, mdt)

    def sync_build(self):
        path = self.model_name
        self.model = Actor(path, {'anim': path + '-' + self.model_suff})
        self.model.reparent_to(render)
        self.model.set_pos(self.pos)
        self.model.loop('anim')
        self.model.setPlayRate(.5, 'anim')

    def destroy(self):
        self.model = self.model.remove_node()
        Gfx.destroy(self)
