class Library(object):

    task_cont = None

    @staticmethod
    def configure(): pass

    @property
    def runtime(self): pass

    @property
    def build_version(self): pass

    @property
    def curr_path(self): pass

    def send(self, msg): pass

    def do_later(self, time, mth, args=[]): pass

    def add_task(self, mth, priority=0): pass

    def remove_task(self, tsk): pass

    def init(self, green=(.2, .8, .2, 1), red=(.8, .2, .2, 1)): pass

    def load_font(self, fpath, outline=True): pass

    def log(self, msg): pass

    def lib_version(self): pass

    def lib_commit(self): pass

    def phys_version(self): pass

    def user_appdata_dir(self): pass

    def driver_vendor(self): pass

    def driver_renderer(self): pass

    def driver_shader_version_major(self): pass

    def driver_shader_version_minor(self): pass

    def driver_version(self): pass

    def driver_version_major(self): pass

    def driver_version_minor(self): pass

    def fullscreen(self): pass

    def resolution(self): pass

    def set_volume(self, vol): pass
