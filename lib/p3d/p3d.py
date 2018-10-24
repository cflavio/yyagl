import sys
from os.path import exists
from os import getcwd
from panda3d.core import loadPrcFileData, Texture, TextPropertiesManager, \
    TextProperties, PandaSystem, Filename, WindowProperties
from panda3d.bullet import get_bullet_version
from direct.showbase.ShowBase import ShowBase
from direct.showbase.DirectObject import DirectObject
from direct.task.Task import Task
from direct.directnotify.DirectNotify import DirectNotify


class LibShowBase(ShowBase): pass


class LibP3d(DirectObject):

    task_cont = Task.cont
    runtime = not exists('main.py')

    def __init__(self):
        DirectObject.__init__(self)
        self.__end_cb = self.__notify = None

    @staticmethod
    def configure():
        loadPrcFileData('', 'notify-level-ya2 info')

    @staticmethod
    def fixpath(path):
        if sys.platform == 'win32':
            if path.startswith('/'): path = path[1] + ':\\' + path[3:]
            path = path.replace('/', '\\')
        return path

    @staticmethod
    def p3dpath(path): return Filename.fromOsSpecific(path)

    def last_frame_dt(self): return globalClock.get_dt()

    @property
    def build_version(self):
        if base.appRunner:
            package = base.appRunner.p3dInfo.FirstChildElement('package')
            #  first_child_element not in panda3d.core.TiXmlDocument
            return package.Attribute('version')
            #  attribute not in panda3d.core.TiXmlDocument
        else:
            return 'deploy-ng'

    @property
    def curr_path(self):
        if base.appRunner:
            return base.appRunner.p3dFilename.get_dirname()
        else:
            return getcwd()

    def send(self, msg): return messenger.send(msg)

    def do_later(self, time, meth, args=[]):
        return taskMgr.doMethodLater(
            time, lambda meth, args: meth(*args), meth.__name__, [meth, args])

    def add_task(self, mth, priority=0):
        return taskMgr.add(mth, mth.__name__, priority)

    def remove_task(self, tsk):
        taskMgr.remove(tsk)

    def init(self, green=(.2, .8, .2, 1), red=(.8, .2, .2, 1), end_cb=None):
        LibShowBase()
        base.disableMouse()
        self.__end_cb = end_cb
        self.__notify = DirectNotify().newCategory('ya2')
        self.__init_win()
        self.__init_fonts(green, red)
        base.a2dTopQuarter = base.aspect2d.attachNewNode('a2dTopQuarter')
        base.a2dTopQuarter.setPos(base.a2dLeft / 2, 0, base.a2dTop)
        base.a2dTopThirdQuarter = \
            base.aspect2d.attachNewNode('a2dTopThirdQuarter')
        base.a2dTopThirdQuarter.setPos(base.a2dRight / 2, 0, base.a2dTop)
        base.a2dCenterQuarter = base.aspect2d.attachNewNode('a2dCenterQuarter')
        base.a2dCenterQuarter.setPos(base.a2dLeft / 2, 0, 0)
        base.a2dCenterThirdQuarter = \
            base.aspect2d.attachNewNode('a2dCenterThirdQuarter')
        base.a2dCenterThirdQuarter.setPos(base.a2dRight / 2, 0, 0)
        base.a2dBottomQuarter = base.aspect2d.attachNewNode('a2dBottomQuarter')
        base.a2dBottomQuarter.setPos(base.a2dLeft / 2, 0, base.a2dBottom)
        base.a2dBottomThirdQuarter = \
            base.aspect2d.attachNewNode('a2dBottomThirdQuarter')
        base.a2dBottomThirdQuarter.setPos(base.a2dRight / 2, 0, base.a2dBottom)
        self.accept('aspectRatioChanged', self.on_aspect_ratio_changed)

    @staticmethod
    def on_aspect_ratio_changed():
        base.a2dTopQuarter.setPos(base.a2dLeft / 2, 0, base.a2dTop)
        base.a2dTopThirdQuarter.setPos(base.a2dRight / 2, 0, base.a2dTop)
        base.a2dBottomQuarter.setPos(base.a2dLeft / 2, 0, base.a2dBottom)
        base.a2dBottomThirdQuarter.setPos(base.a2dRight / 2, 0, base.a2dBottom)

    @staticmethod
    def has_window(): return bool(base.win)

    @property
    def resolution(self):
        win_prop = base.win.get_properties()
        return win_prop.get_x_size(), win_prop.get_y_size()

    @property
    def resolutions(self):
        d_i = base.pipe.get_display_information()

        def res(idx):
            return d_i.get_display_mode_width(idx), \
                d_i.get_display_mode_height(idx)
        ret = [res(idx) for idx in range(d_i.get_total_display_modes())]
        return ret if ret else [self.resolution]

    @staticmethod
    def toggle_fullscreen():
        props = WindowProperties()
        props.set_fullscreen(not base.win.is_fullscreen())
        base.win.request_properties(props)

    @staticmethod
    def set_resolution(res, fullscreen=None):
        props = WindowProperties()
        props.set_size(res)
        if fullscreen: props.set_fullscreen(True)
        base.win.request_properties(props)

    def __init_win(self):
        if base.win: base.win.set_close_request_event('window-closed')
        # not headless
        self.accept('window-closed', self.__on_end)

    @staticmethod
    def __init_fonts(green=(.2, .8, .2, 1), red=(.8, .2, .2, 1)):
        tp_mgr = TextPropertiesManager.get_global_ptr()
        for namecol, col in zip(['green', 'red'], [green, red]):
            props = TextProperties()
            props.set_text_color(col)
            tp_mgr.set_properties(namecol, props)
        tp_small = TextProperties()
        tp_small.set_text_scale(.46)
        tp_mgr.set_properties('small', tp_small)
        tp_small = TextProperties()
        tp_small.set_text_scale(.72)
        tp_mgr.set_properties('smaller', tp_small)
        tp_italic = TextProperties()
        tp_italic.set_slant(.2)
        tp_mgr.set_properties('italic', tp_italic)

    def __on_end(self):
        base.closeWindow(base.win)
        if self.__end_cb: self.__end_cb()
        sys.exit()

    def load_font(self, fpath, outline=True):
        font = base.loader.loadFont(fpath)
        font.set_pixels_per_unit(60)
        font.set_minfilter(Texture.FTLinearMipmapLinear)
        if outline: font.set_outline((0, 0, 0, 1), .8, .2)
        return font

    def log(self, msg): self.__notify.info(msg)

    @staticmethod
    def version(): return PandaSystem.get_version_string()

    def lib_commit(self): return PandaSystem.get_git_commit()

    def phys_version(self): return get_bullet_version()

    def user_appdata_dir(self): return Filename.get_user_appdata_directory()

    def driver_vendor(self): return base.win.get_gsg().get_driver_vendor()

    def driver_renderer(self): return base.win.get_gsg().get_driver_renderer()

    def driver_shader_version_major(self):
        return base.win.get_gsg().get_driver_shader_version_major()

    def driver_shader_version_minor(self):
        return base.win.get_gsg().get_driver_shader_version_minor()

    def driver_version(self): return base.win.get_gsg().get_driver_version()

    def driver_version_major(self):
        return base.win.get_gsg().get_driver_version_major()

    def driver_version_minor(self):
        return base.win.get_gsg().get_driver_version_minor()

    def fullscreen(self): return base.win.get_properties().get_fullscreen()

    def set_volume(self, vol): return base.sfxManagerList[0].set_volume(vol)

    @staticmethod
    def get_mouse():
        mwn = base.mouseWatcherNode
        if not mwn.hasMouse(): return
        return mwn.get_mouse_x(), mwn.get_mouse_y()

    @staticmethod
    def aspect_ratio(): return base.getAspectRatio()

    @staticmethod
    def set_std_cursor(show):
        props = WindowProperties()
        props.set_cursor_hidden(not show)
        base.win.requestProperties(props)

    @staticmethod
    def find_geoms(model, name):  # no need to be cached
        geoms = model.node.find_all_matches('**/+GeomNode')
        is_nm = lambda geom: geom.get_name().startswith(name)
        named_geoms = [geom for geom in geoms if is_nm(geom)]
        return [ng for ng in named_geoms if name in ng.get_name()]

    @staticmethod
    def load_sfx(fpath, loop=False):
        sfx = loader.loadSfx(fpath)
        sfx.set_loop(loop)
        return sfx
