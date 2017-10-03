from panda3d.core import loadPrcFileData
from .log import LogMgr


class Cfg(object):

    def __init__(
            self, fps=False, win_size='1280 720', win_orig=None,
            win_title='Ya2', fullscreen=False, sync_video=True,
            antialiasing=False, profiling=False, pyprof_percall=False,
            mt_render=False, model_path='assets/models', lang='en',
            lang_path='assets/locale', lang_domain='ya2_game',
            languages=['English', 'Italiano'], shaders_dev=False, gamma=1.0,
            menu_joypad=True, cursor_hidden=False, cursor_path='',
            cursor_scale=(1, 1, 1), cursor_hotspot=(0, 0), volume=1):
        self.fps = fps
        self.win_size = win_size
        self.win_title = win_title
        self.win_orig = win_orig
        self.fullscreen = fullscreen
        self.sync_video = sync_video
        self.antialiasing = antialiasing
        self.multithreaded_render = mt_render
        self.profiling = profiling
        self.pyprof_percall = pyprof_percall
        self.model_path = model_path
        self.lang = lang
        self.lang_path = lang_path
        self.lang_domain = lang_domain
        self.languages = languages
        self.shaders_dev = shaders_dev
        self.gamma = gamma
        self.menu_joypad = menu_joypad
        self.cursor_hidden = cursor_hidden
        self.cursor_path = cursor_path
        self.cursor_scale = cursor_scale
        self.cursor_hotspot = cursor_hotspot
        self.volume = volume
        self.__configure()

    @staticmethod
    def __set(key, value):
        loadPrcFileData('', key + ' ' + str(value))

    def __configure(self):
        self.__set('texture-anosotropic-degree', 2)
        self.__set('texture-magfilter', 'linear')
        self.__set('texture-minfilter', 'mipmap')
        self.__set('gl-coordinate-system', 'default')
        self.__set('textures-power-2', 'none')
        self.__set('show-frame-rate-meter', int(self.fps))
        self.__set('hardware-animated-vertices', 'true')
        self.__set('basic-shaders-only', 'false')
        if self.win_size:
            self.__set('win-size', self.win_size)
        if self.win_orig:
            self.__set('win-origin', self.win_orig)
        self.__set('window-title', self.win_title)
        self.__set('cursor-hidden', int(self.cursor_hidden))
        self.__set('sync-video', int(self.sync_video))
        if self.antialiasing:
            self.__set('framebuffer-multisample', 1)
            self.__set('multisamples', 2)
        if self.multithreaded_render:
            self.__set('threading-model', '/Draw')
        if self.profiling:
            self.__set('want-pstats', 1)
            self.__set('task-timer-verbose', 1)
            self.__set('pstats-tasks', 1)
            self.__set('gl-finish', 1)
            self.__set('pstats-host', '127.0.0.1')
