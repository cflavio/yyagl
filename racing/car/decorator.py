from direct.actor.Actor import Actor
from yyagl.gameobject import GameObject


class Decorator(GameObject):

    def __init__(self, fpath, parent):
        GameObject.__init__(self)
        self.gfx_np = self.eng.load_model(fpath, anim={'anim': fpath + '-Anim'})
        self.gfx_np.loop('anim')
        #self.gfx_np.flatten_light()
        self.gfx_np.reparent_to(parent)
        self.gfx_np.set_scale(1.5)
        self.gfx_np.set_pos((0, 0, 1.5))

    def destroy(self):
        self.gfx_np.cleanup()
        self.gfx_np = self.gfx_np.remove_node()
        GameObject.destroy(self)
