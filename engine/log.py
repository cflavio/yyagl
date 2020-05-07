from logging import basicConfig, info, INFO
#from datetime import datetime
from pprint import pprint
from traceback import print_stack
from sys import version_info
# from platform import system, release, architecture, platform, processor, \
#     version, machine
# from multiprocessing import cpu_count
from yyagl.gameobject import Colleague


basicConfig(level=INFO, format='%(asctime)s %(message)s', datefmt='%H:%M:%S')


class LogMgrBase(Colleague):  # headless log manager

    @staticmethod
    def init_cls():
        return LogMgr if base.win else LogMgrBase

    def __init__(self, mediator):
        Colleague.__init__(self, mediator)
        self.log_cfg()

    def log(self, msg, verbose=False):
        if verbose and not self.eng.cfg.dev_cfg.verbose_log: return
        info(msg)

    def log_cfg(self):
        messages = ['version: ' + self.eng.logic.version]
        # os_info = (system(), release(), version())
        # messages += ['operative system: %s %s %s' % os_info]
        # messages += ['architecture: ' + str(architecture())]
        # messages += ['machine: ' + machine()]
        # messages += ['platform: ' + platform()]
        # messages += ['processor: ' + processor()]
        # try:
        #     messages += ['cores: ' + str(cpu_count())]
        # except NotImplementedError:  # on Windows
        #     messages += ['cores: not implemented']
        lib_ver = self.eng.lib.version
        try:
            import psutil
            mem = psutil.virtual_memory().total / 1000000000.0
            messages += ['memory: %s GB' % round(mem, 2)]
        except ImportError: info("can't import psutil")  # windows
        lib_commit = self.eng.lib.lib_commit
        py_ver = [str(elm) for elm in version_info[:3]]
        messages += ['python version: %s' % '.'.join(py_ver)]
        messages += ['panda version: %s %s' % (lib_ver, lib_commit)]
        messages += ['bullet version: ' + str(self.eng.lib.phys_version)]
        messages += ['appdata: ' + str(self.eng.lib.user_appdata_dir)]
        if base.win: print(base.win.get_keyboard_map())
        list(map(self.log, messages))

    @staticmethod
    def log_tasks():
        info('tasks: %s' % taskMgr.getAllTasks())
        info('do-laters: %s' % taskMgr.getDoLaters())

    @staticmethod
    def plog(obj):
        print('\n\n')
        print_stack()
        pprint(obj)
        print('\n\n')


class LogMgr(LogMgrBase):

    def log_cfg(self):
        LogMgrBase.log_cfg(self)
        messages = [self.eng.lib.driver_vendor]
        messages += [self.eng.lib.driver_renderer]
        shad_maj = self.eng.lib.driver_shader_version_major
        shad_min = self.eng.lib.driver_shader_version_minor
        messages += ['shader: {maj}.{min}'.format(maj=shad_maj, min=shad_min)]
        messages += [self.eng.lib.driver_version]
        drv_maj = self.eng.lib.driver_version_major
        drv_min = self.eng.lib.driver_version_minor
        drv = 'driver version: {maj}.{min}'
        messages += [drv.format(maj=drv_maj, min=drv_min)]
        messages += ['fullscreen: ' + str(self.eng.lib.fullscreen)]
        res_x, res_y = self.eng.lib.resolution
        res_tmpl = 'resolution: {res_x}x{res_y}'
        messages += [res_tmpl.format(res_x=res_x, res_y=res_y)]
        list(map(self.log, messages))
