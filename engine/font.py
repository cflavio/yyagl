from panda3d.core import Texture, TextPropertiesManager, TextProperties
from ..singleton import Singleton


class FontMgr(object):

    __metaclass__ = Singleton

    def __init__(self, color_green=(.25, .75, .25, 1), color_red=(.75, .25, .25, 1)):
        self.__fonts = {}
        tp_mgr = TextPropertiesManager.getGlobalPtr()
        for namecol, col in zip(['green', 'red'], [color_green, color_red]):
            props = TextProperties()
            props.setTextColor(col)
            tp_mgr.setProperties(namecol, props)

    def load_font(self, path, outline=True):
        if path not in self.__fonts:
            self.__fonts[path] = eng.base.loader.loadFont(path)
            self.__fonts[path].set_pixels_per_unit(60)
            self.__fonts[path].set_minfilter(Texture.FTLinearMipmapLinear)
            outline and self.__fonts[path].set_outline((0, 0, 0, 1), .8, .2)
        return self.__fonts[path]
