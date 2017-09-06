from datetime import datetime
from platform import system, release, architecture, platform, processor, \
    version, machine
from multiprocessing import cpu_count
from panda3d.core import loadPrcFileData, PandaSystem, Filename
from panda3d.bullet import get_bullet_version
from direct.directnotify.DirectNotify import DirectNotify
from yyagl.gameobject import GameObject


class LogMgrBase(GameObject):

    @staticmethod
    def init_cls():
        return LogMgr if base.win else LogMgrBase

    def __init__(self):
        self.__notify = DirectNotify().newCategory('ya2')
        self.log_conf()

    @staticmethod
    def configure():
        loadPrcFileData('', 'notify-level-ya2 info')

    def log(self, msg):
        time = datetime.now().strftime("%H:%M:%S")
        self.__notify.info('{time} {msg}'.format(time=time, msg=msg))

    def log_conf(self):
        self.log('version: ' + self.eng.logic.version)
        os_info = (system(), release(), version())
        self.log('operative system: %s %s %s' % os_info)
        self.log('architecture: ' + str(architecture()))
        self.log('machine: ' + machine())
        self.log('platform: ' + platform())
        self.log('processor: ' + processor())
        try:
            self.log('cores: ' + str(cpu_count()))
        except NotImplementedError:  # on Windows
            self.log('cores: not implemented')
        panda_ver = PandaSystem.get_version_string()
        panda_git = PandaSystem.get_git_commit()
        self.log('panda version: %s %s' % (panda_ver, panda_git))
        self.log('bullet version: ' + str(get_bullet_version()))
        self.log('appdata: ' + str(Filename.get_user_appdata_directory()))


class LogMgr(LogMgrBase):

    def log_conf(self):
        LogMgrBase.log_conf(self)
        gsg = self.eng.base.win.get_gsg()
        self.log(gsg.get_driver_vendor())
        self.log(gsg.get_driver_renderer())
        shad_maj = gsg.get_driver_shader_version_major()
        shad_min = gsg.get_driver_shader_version_minor()
        self.log('shader: {maj}.{min}'.format(maj=shad_maj, min=shad_min))
        self.log(gsg.get_driver_version())
        drv_maj = gsg.get_driver_version_major()
        drv_min = gsg.get_driver_version_minor()
        drv = 'driver version: {maj}.{min}'
        self.log(drv.format(maj=drv_maj, min=drv_min))
        props = self.eng.base.win.get_properties()
        self.log('fullscreen: ' + str(props.get_fullscreen()))
        res_x, res_y = props.get_x_size(), props.get_y_size()
        res_tmpl = 'resolution: {res_x}x{res_y}'
        self.log(res_tmpl.format(res_x=res_x, res_y=res_y))
