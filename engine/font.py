from yyagl.gameobject import GameObject


class FontMgr(GameObject):

    def __init__(self):
        GameObject.__init__(self)
        self.__fonts = {}

    def load_font(self, fpath, outline=True):
        if fpath not in self.__fonts:
            self.__fonts[fpath] = self.eng.lib.load_font(fpath, outline)
        return self.__fonts[fpath]

    def destroy(self):
        self.fonts = None
        GameObject.destroy(self)