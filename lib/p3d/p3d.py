import sys
from logging import info
from os.path import exists, dirname
from os import getcwd, _exit
from pathlib import Path
from panda3d.core import loadPrcFileData, Texture, TextPropertiesManager, \
    TextProperties, PandaSystem, Filename, WindowProperties
from panda3d.bullet import get_bullet_version
from direct.showbase.ShowBase import ShowBase
from direct.showbase.DirectObject import DirectObject
from direct.task.Task import Task


class LibShowBase(ShowBase): pass


class LibP3d(DirectObject):

    task_cont = Task.cont

    def __init__(self):
        DirectObject.__init__(self)
        self.__end_cb = self.__notify = None
        self.__logged_keys = {}

    @staticmethod
    def runtime(): return not exists('main.py')

    @staticmethod
    def configure():
        loadPrcFileData('', 'notify-level-ya2 info')
        # loadPrcFileData('', 'gl-version 3 2')

    @staticmethod
    def fixpath(path):
        if sys.platform == 'win32':
            if path.startswith('/'): path = path[1] + ':\\' + path[3:]
            path = path.replace('/', '\\')
        return path

    @staticmethod
    def p3dpath(path): return Filename.fromOsSpecific(path)

    @property
    def last_frame_dt(self): return globalClock.get_dt()

    @property
    def build_version(self):
        with open(self.curr_path + '/assets/bld_version.txt') as fver:
            return fver.read().strip()


    @property
    def curr_path(self):
        if sys.platform == 'darwin':
            return dirname(__file__) + '/../Resources/'
        # return dirname(__file__)
        par_path = str(Path(__file__).parent.absolute())
        is_appimage = par_path.startswith('/tmp/.mount_Yorg')
        is_appimage = is_appimage and par_path.endswith('/usr/bin')
        if is_appimage:
            return str(Path(par_path).absolute())
        is_snap = par_path.startswith('/snap/')
        is_snap = is_snap and par_path.endswith('/x1')
        if is_snap:
            return str(Path(par_path).absolute())
        #return getcwd()
        curr_path = dirname(__file__)
        info('current path: %s' % curr_path)
        return curr_path

    @staticmethod
    def send(msg): return messenger.send(msg)

    @staticmethod
    def do_later(time, meth, args=None):
        args = args or []
        return taskMgr.doMethodLater(
            time, lambda meth, args: meth(*args), meth.__name__, [meth, args])

    @staticmethod
    def add_task(mth, priority=0):
        return taskMgr.add(mth, mth.__name__, priority)

    @staticmethod
    def remove_task(tsk): taskMgr.remove(tsk)

    def init(self, green=(.2, .8, .2, 1), red=(.8, .2, .2, 1), end_cb=None):
        LibShowBase()
        base.disableMouse()
        self.__end_cb = end_cb
        self.__init_win()
        self.__init_fonts(green, red)
        self.__set_roots()
        self.accept('aspectRatioChanged', self.on_aspect_ratio_changed)

    @staticmethod
    def __set_roots():
        base.a2dTopQuarter = base.aspect2d.attachNewNode('a2dTopQuarter')
        base.a2dTopQuarter.set_pos(base.a2dLeft / 2, 0, base.a2dTop)
        base.a2dTopThirdQuarter = \
            base.aspect2d.attachNewNode('a2dTopThirdQuarter')
        base.a2dTopThirdQuarter.set_pos(base.a2dRight / 2, 0, base.a2dTop)
        base.a2dCenterQuarter = base.aspect2d.attachNewNode('a2dCenterQuarter')
        base.a2dCenterQuarter.set_pos(base.a2dLeft / 2, 0, 0)
        base.a2dCenterThirdQuarter = \
            base.aspect2d.attachNewNode('a2dCenterThirdQuarter')
        base.a2dCenterThirdQuarter.set_pos(base.a2dRight / 2, 0, 0)
        base.a2dBottomQuarter = base.aspect2d.attachNewNode('a2dBottomQuarter')
        base.a2dBottomQuarter.set_pos(base.a2dLeft / 2, 0, base.a2dBottom)
        base.a2dBottomThirdQuarter = \
            base.aspect2d.attachNewNode('a2dBottomThirdQuarter')
        base.a2dBottomThirdQuarter.set_pos(
            base.a2dRight / 2, 0, base.a2dBottom)

    @staticmethod
    def on_aspect_ratio_changed():
        base.a2dTopQuarter.set_pos(base.a2dLeft / 2, 0, base.a2dTop)
        base.a2dTopThirdQuarter.set_pos(base.a2dRight / 2, 0, base.a2dTop)
        base.a2dBottomQuarter.set_pos(base.a2dLeft / 2, 0, base.a2dBottom)
        base.a2dBottomThirdQuarter.set_pos(
            base.a2dRight / 2, 0, base.a2dBottom)

    @property
    def has_window(self): return bool(base.win)

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
        for namesize, col in zip(['small', 'smaller'], [.46, .72]):
            props = TextProperties()
            props.set_text_scale(.46)
            tp_mgr.set_properties(namesize, props)
        tp_italic = TextProperties()
        tp_italic.set_slant(.2)
        tp_mgr.set_properties('italic', tp_italic)

    def __on_end(self):
        base.closeWindow(base.win)
        if self.__end_cb: self.__end_cb()
        _exit(0)

    @staticmethod
    def load_font(filepath, outline=True):
        font = base.loader.loadFont(filepath)
        font.set_pixels_per_unit(60)
        font.set_minfilter(Texture.FTLinearMipmapLinear)
        if outline: font.set_outline((0, 0, 0, 1), .8, .2)
        return font

    @staticmethod
    def log(msg): print(msg)

    @property
    def version(self): return PandaSystem.get_version_string()

    @property
    def lib_commit(self): return PandaSystem.get_git_commit()

    @property
    def phys_version(self): return get_bullet_version()

    @property
    def user_appdata_dir(self): return Filename.get_user_appdata_directory()

    @property
    def driver_vendor(self): return base.win.get_gsg().get_driver_vendor()

    @property
    def driver_renderer(self): return base.win.get_gsg().get_driver_renderer()

    @property
    def driver_shader_version_major(self):
        return base.win.get_gsg().get_driver_shader_version_major()

    @property
    def driver_shader_version_minor(self):
        return base.win.get_gsg().get_driver_shader_version_minor()

    @property
    def driver_version(self): return base.win.get_gsg().get_driver_version()

    @property
    def driver_version_major(self):
        return base.win.get_gsg().get_driver_version_major()

    @property
    def driver_version_minor(self):
        return base.win.get_gsg().get_driver_version_minor()

    @property
    def fullscreen(self): return base.win.get_properties().get_fullscreen()

    @property
    def volume(self): return base.sfxManagerList[0].get_volume()

    @volume.setter
    def volume(self, vol): base.sfxManagerList[0].set_volume(vol)

    @property
    def mousepos(self):
        mwn = base.mouseWatcherNode
        if not mwn.hasMouse(): return 0, 0
        return mwn.get_mouse_x(), mwn.get_mouse_y()

    @property
    def aspect_ratio(self): return base.getAspectRatio()

    @staticmethod
    def set_icon(filename):
        props = WindowProperties()
        props.set_icon_filename(filename)
        base.win.requestProperties(props)

    @staticmethod
    def __set_std_cursor(show):
        props = WindowProperties()
        props.set_cursor_hidden(not show)
        base.win.requestProperties(props)

    @staticmethod
    def show_std_cursor(): LibP3d.__set_std_cursor(True)

    @staticmethod
    def hide_std_cursor(): LibP3d.__set_std_cursor(False)

    @staticmethod
    def find_geoms(model, name):  # no need to be cached
        geoms = model.node.find_all_matches('**/+GeomNode')
        is_nm = lambda geom: geom.get_name().startswith(name)
        named_geoms = [geom for geom in geoms if is_nm(geom)]
        return [ng for ng in named_geoms if name in ng.get_name()]

    @staticmethod
    def load_sfx(filepath, loop=False):
        sfx = loader.loadSfx(filepath)
        sfx.set_loop(loop)
        return sfx

    def remap_code(self, key):
        kmap = base.win.get_keyboard_map()
        for i in range(kmap.get_num_buttons()):
            if key.lower() == kmap.get_mapped_button_label(i).lower():
                self.__log_key(
                    'code mapping %s to key %s' %
                    (key, kmap.get_mapped_button(i)), key,
                    kmap.get_mapped_button(i))
                return kmap.get_mapped_button(i)
        for i in range(kmap.get_num_buttons()):
            if key.lower() == kmap.get_mapped_button(i).get_name().lower():
                self.__log_key(
                    'code mapping %s to key %s' %
                    (key, kmap.get_mapped_button(i)), key,
                    kmap.get_mapped_button(i))
                return kmap.get_mapped_button(i)
        self.__log_key('not found a code mapping for %s' %
                       key, key, 'not_found')
        return key

    def remap_str(self, key):
        kmap = base.win.get_keyboard_map()
        for i in range(kmap.get_num_buttons()):
            if key.lower() == kmap.get_mapped_button_label(i).lower():
                self.__log_key(
                    'string mapping %s to key %s' %
                    (key, kmap.get_mapped_button(i).get_name()), key,
                    kmap.get_mapped_button(i).get_name())
                return kmap.get_mapped_button(i).get_name()
        for i in range(kmap.get_num_buttons()):
            if key.lower() == kmap.get_mapped_button(i).get_name().lower():
                self.__log_key(
                    'string mapping %s to key %s' %
                    (key, kmap.get_mapped_button(i).get_name()), key,
                    kmap.get_mapped_button(i).get_name())
                return kmap.get_mapped_button(i).get_name()
        self.__log_key('not found a string mapping for %s' %
                       key, key, kmap.get_mapped_button(i).get_name())
        return key

    def __log_key(self, msg, key1, key2):
        if key1 in self.__logged_keys and self.__logged_keys[key1] == key2:
            return
        self.__logged_keys[key1] = key2
        print(msg)

    def destroy(self): pass
