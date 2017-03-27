from panda3d.core import Texture, TextPropertiesManager, TextProperties
from ..gameobject import Colleague


class FontMgr(Colleague):

    def __init__(self, mdt):
        Colleague.__init__(self, mdt)
        self.__fonts = {}
        tp_mgr = TextPropertiesManager.getGlobalPtr()
        colors = [(.75, .25, .25, 1), (.25, .75, .25, 1)]
        for namecol, col in zip(['red', 'green'], colors):
            _tp = TextProperties()
            _tp.setTextColor(col)
            tp_mgr.setProperties(namecol, _tp)

    def load_font(self, path):
        if path not in self.__fonts:
            self.__fonts[path] = eng.base.loader.loadFont(path)
            self.__fonts[path].setPixelsPerUnit(60)
            self.__fonts[path].setMinfilter(Texture.FTLinearMipmapLinear)
            self.__fonts[path].setOutline((0, 0, 0, 1), .8, .2)
        return self.__fonts[path]
