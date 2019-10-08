from direct.actor.Actor import Actor
from yyagl.gameobject import GfxColleague


class BonusGfx(GfxColleague):

    def __init__(self, mediator, pos, model_path, anim_suff):
        self.model = None
        self.pos = pos
        self.model_path = model_path
        self.anim_suff = anim_suff
        GfxColleague.__init__(self, mediator)
        path = self.model_path
        self.model = Actor(path, {'anim': path + '-' + self.anim_suff})
        self.model.reparent_to(render)
        self.model.set_pos(self.pos)
        self.model.loop('anim')
        self.model.setPlayRate(.5, 'anim')
        self.model.set_depth_offset(1)

    def destroy(self):
        self.model.cleanup()
        self.model = self.model.remove_node()
        GfxColleague.destroy(self)
