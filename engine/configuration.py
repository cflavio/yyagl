from panda3d.core import load_prc_file_data
from yyagl.lib.builder import LibP3d


class GuiCfg(object):

    def __init__(self, fps=False, win_size='1280 720', win_orig=None,
                 win_title='yyagl', fullscreen=False, sync_video=None,
                 antialiasing=False, shaders=True, volume=1, fixed_fps=0):
        self.fps = fps
        self.win_size = win_size
        self.win_title = win_title
        self.win_orig = win_orig
        self.fullscreen = fullscreen
        self.sync_video = LibP3d.runtime() if sync_video is None \
            else sync_video
        self.antialiasing = antialiasing
        self.shaders = shaders
        self.volume = volume
        self.fixed_fps = fixed_fps


class ProfilingCfg(object):

    def __init__(self, profiling=False, pyprof_percall=False):
        self.profiling = profiling  # profiling with panda3d's tools
        self.pyprof_percall = pyprof_percall


class LangCfg(object):

    def __init__(self, lang='en', lang_path='assets/locale',
                 lang_domain='yyagl_game', languages=[('English', 'en')]):
        self.lang = lang
        self.lang_path = lang_path
        self.lang_domain = lang_domain
        self.languages = languages


class CursorCfg(object):

    def __init__(self, cursor_hidden=False, cursor_path='',
                 cursor_scale=(1, 1, 1), cursor_hotspot=(0, 0)):
        self.cursor_hidden = cursor_hidden
        self.cursor_path = cursor_path
        self.cursor_scale = cursor_scale
        self.cursor_hotspot = cursor_hotspot


class DevCfg(object):

    def __init__(self, mt_render=False, model_path='assets/models',
                 shaders_dev=False, gamma=1.0, menu_joypad=True, verbose='',
                 verbose_log=False, xmpp_server='', start_wp='', port=9099,
                 server='localhost:9098', srgb=False, opengl_3_2=False):
        self.multithreaded_render = mt_render  # multithreaded rendering
        self.model_path = model_path
        self.shaders_dev = shaders_dev
        self.gamma = gamma
        self.menu_joypad = menu_joypad
        self.verbose = verbose
        self.verbose_log = verbose_log
        self.xmpp_server = xmpp_server
        self.port = port
        self.server = server
        self.start_wp = start_wp
        self.srgb = srgb
        self.opengl_3_2 = opengl_3_2


class Cfg(object):

    def __init__(self, gui_cfg=None, profiling_cfg=None, lang_cfg=None,
                 cursor_cfg=None, dev_cfg=None):
        self.gui_cfg = gui_cfg or GuiCfg()
        self.profiling_cfg = profiling_cfg or ProfilingCfg()
        self.lang_cfg = lang_cfg or LangCfg()
        self.cursor_cfg = cursor_cfg or CursorCfg()
        self.dev_cfg = dev_cfg or DevCfg()
        self.__configure()

    @staticmethod
    def __set(key, val): load_prc_file_data('', key + ' ' + str(val))

    def __configure(self):
        cfginfo = [
            ('texture-anosotropic-degree', 2),
            ('texture-magfilter', 'linear'),
            ('texture-minfilter', 'mipmap'),
            ('gl-coordinate-system', 'default'),
            ('textures-power-2', 'none'),
            ('show-frame-rate-meter', int(self.gui_cfg.fps)),
            ('hardware-animated-vertices', 'true'),
            ('x-init-threads','true'),  # temp workaround 4 mtrendering (linux)
            ('basic-shaders-only', 'false'),
            ('default-model-extension', '.bam')]
        if self.gui_cfg.win_size:
            cfginfo += [('win-size', self.gui_cfg.win_size)]
        if self.gui_cfg.win_orig:
            cfginfo += [('win-origin', self.gui_cfg.win_orig)]
        if self.dev_cfg.srgb:
            cfginfo += [('framebuffer-srgb', 'true')]
        if self.dev_cfg.opengl_3_2:
            cfginfo += [('gl-version', '3 2')]
        cfginfo += [
            ('window-title', self.gui_cfg.win_title),
            ('cursor-hidden', int(self.cursor_cfg.cursor_hidden)),
            ('sync-video', int(self.gui_cfg.sync_video)),
            ('framebuffer-multisample', 1),
            ('multisamples', 2)]
        if self.dev_cfg.multithreaded_render:
            cfginfo += [('threading-model', '/Draw')]
        if self.profiling_cfg.profiling:
            cfginfo += [
                ('want-pstats', 1),
                ('task-timer-verbose', 1),
                ('pstats-tasks', 1),
                ('gl-finish', 1),
                ('pstats-host', '127.0.0.1')]
        for verb in self.dev_cfg.verbose.split(';'):
            if not verb: continue
            verb_el = verb.strip().split()
            if verb_el[0] == 'direct':
                cfginfo += [
                    ('default-directnotify-level', verb_el[1])]
            elif verb_el[0] == 'panda':
                cfginfo += [
                    ('notify-level', verb_el[1])]
            else:
                cfginfo += [
                    ('notify-level-' + verb_el[0], verb_el[1])]
        list(map(lambda args: self.__set(*args), cfginfo))
