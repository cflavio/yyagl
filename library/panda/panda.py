import sys
from os.path import exists
from panda3d.core import loadPrcFileData, Texture, TextPropertiesManager, \
    TextProperties, PandaSystem, Filename
from panda3d.bullet import get_bullet_version
from direct.showbase.ShowBase import ShowBase
from direct.showbase.DirectObject import DirectObject
from direct.task.Task import Task
from direct.directnotify.DirectNotify import DirectNotify
from ..library import Library


class LibShowBase(ShowBase): pass


class LibraryPanda3D(Library, DirectObject):

    task_cont = Task.cont
    runtime = not exists('main.py')

    @staticmethod
    def configure():
        loadPrcFileData('', 'notify-level-ya2 info')

    def last_frame_dt(self): return globalClock.get_dt()

    @property
    def build_version(self):
        package = base.appRunner.p3dInfo.FirstChildElement('package')
        #  first_child_element not in panda3d.core.TiXmlDocument
        return package.Attribute('version')
        #  attribute not in panda3d.core.TiXmlDocument

    @property
    def curr_path(self):
        return base.appRunner.p3dFilename.get_dirname()

    def send(self, msg): return messenger.send(msg)

    def do_later(self, time, meth, args=[]):
        return taskMgr.doMethodLater(time, lambda meth, args: meth(*args), meth.__name__, [meth, args])

    def add_task(self, mth, priority=0):
        return taskMgr.add(mth, mth.__name__, priority)

    def remove_task(self, tsk):
        return taskMgr.remove(tsk)

    def init(self, green=(.2, .8, .2, 1), red=(.8, .2, .2, 1), end_cb=None):
        LibShowBase()
        self.__end_cb = end_cb
        self.__notify = DirectNotify().newCategory('ya2')
        self.__init_win()
        self.__init_fonts(green, red)

    def __init_win(self):
        if base.win: base.win.set_close_request_event('window-closed')
        # not headless
        self.accept('window-closed', self.__on_end)

    def __init_fonts(self, green=(.2, .8, .2, 1), red=(.8, .2, .2, 1)):
        tp_mgr = TextPropertiesManager.get_global_ptr()
        for namecol, col in zip(['green', 'red'], [green, red]):
            props = TextProperties()
            props.set_text_color(col)
            tp_mgr.set_properties(namecol, props)

    def __on_end(self):
        base.closeWindow(base.win)
        if self.__end_cb: self.__end_cb()
        sys.exit()

    def load_font(self, fpath, outline=True):
        font = base.loader.loadFont(fpath)
        font.set_pixels_per_unit(60)
        font.set_minfilter(Texture.FTLinearMipmapLinear)
        outline and font.set_outline((0, 0, 0, 1), .8, .2)
        return font

    def log(self, msg): self.__notify.info(msg)

    def lib_version(self): return PandaSystem.get_version_string()

    def lib_commit(self): return PandaSystem.get_git_commit()

    def phys_version(self): return get_bullet_version()

    def user_appdata_dir(self): return Filename.get_user_appdata_directory()

    def driver_vendor(self): return base.win.get_gsg().get_driver_vendor()

    def driver_renderer(self): return base.win.get_gsg().get_driver_renderer()

    def driver_shader_version_major(self): return base.win.get_gsg().get_driver_shader_version_major()

    def driver_shader_version_minor(self): return base.win.get_gsg().get_driver_shader_version_minor()

    def driver_version(self): return base.win.get_gsg().get_driver_version()

    def driver_version_major(self): return base.win.get_gsg().get_driver_version_major()

    def driver_version_minor(self): return base.win.get_gsg().get_driver_version_minor()

    def fullscreen(self): return base.win.get_properties().get_fullscreen()

    def resolution(self): return base.win.get_properties().get_x_size(), base.win.get_properties().get_y_size()

    def set_volume(self, vol): return base.sfxManagerList[0].set_volume(vol)

    @staticmethod
    def find_geoms(model, name):  # no need to be cached
        geoms = model.node.find_all_matches('**/+GeomNode')
        is_nm = lambda geom: geom.get_name().startswith(name)
        named_geoms = [geom for geom in geoms if is_nm(geom)]
        return [ng for ng in named_geoms if name in ng.get_name()]
