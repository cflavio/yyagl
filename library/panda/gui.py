from direct.gui.OnscreenImage import OnscreenImage
from ..igui import IImg


class PandaImg(IImg):

    def __init__(self, fpath, scale=1.0, is_background=False):
        self.img = OnscreenImage(fpath, scale=scale)
        if is_background: self.img.set_bin('background', 10)

    def destroy(self):
        self.img = self.img.destroy()
