from yyagl.gameobject import GameObject
from yyagl.engine.vec import Vec


class Decorator(GameObject):

    def __init__(self, fpath, parent):
        GameObject.__init__(self)
        anim_dct = {'anim': fpath + '-Anim'}
        self.gfx_np = self.eng.load_model(fpath, anim=anim_dct)
        self.gfx_np.loop('anim')
        #self.gfx_np.flatten_light()
        self.gfx_np.reparent_to(parent)
        self.gfx_np.set_scale(1.5)
        self.gfx_np.set_pos(Vec(0, 0, 1.5))

    def destroy(self):
        self.gfx_np.cleanup()
        self.gfx_np = self.gfx_np.remove_node()
        GameObject.destroy(self)
