from .shader import ShaderMgr
from .font import FontMgr


class EngineFacade(object):

    def attach_obs(self, meth, sort=10):  # otherwise MRO picks Engine's attach
        return self.event.attach(meth, sort)

    def detach_obs(self, meth):
        return self.event.detach(meth)

    def attach_node(self, node):
        return self.gfx.root.attachNewNode(node)

    def particle(self, path, parent, render_parent, pos, timeout):
        return self.gfx.particle(path, parent, render_parent, pos, timeout)

    def init_gfx(self):
        return self.gfx.init()

    def clean_gfx(self):
        return self.gfx.clean()

    @staticmethod
    def do_later(time, meth, args=[], pass_tsk=False):
        if pass_tsk:
            return taskMgr.doMethodLater(time, lambda tsk: meth(tsk, *args),
                                         meth.__name__)
        else:
            return taskMgr.doMethodLater(time, lambda tsk: meth(*args),
                                         meth.__name__)

    def remove_do_later(self, tsk):
        self.pause.remove_task(tsk)
        return taskMgr.remove(tsk)

    @staticmethod
    def add_tsk(meth, priority):
        return taskMgr.add(meth, meth.__name__, priority)

    def load_model(self, filename, callback=None, extra_args=[]):
        args = {'callback': callback, 'extraArgs': extra_args}
        return self.gfx.load_model(filename, **(args if callback else {}))

    def set_cam_pos(self, pos):
        return self.base.camera.set_pos(pos)

    @staticmethod
    def load_font(self, font):
        return FontMgr().load_font(font)

    @property
    def version(self):
        return self.logic.version

    @property
    def curr_path(self):
        return self.logic.curr_path

    def open_browser(self, url):
        return self.gui.open_browser(url)

    def toggle_pause(self, show_frm=True):
        return self.pause.logic.toggle(show_frm)

    def play(self, sfx):
        return self.audio.play(sfx)

    def set_volume(self, vol):
        return self.audio.set_volume(vol)

    def show_cursor(self):
        return self.gui.cursor.show()

    def show_standard_cursor(self):
        return self.gui.cursor.show_standard()

    def hide_cursor(self):
        return self.gui.cursor.hide()

    def hide_standard_cursor(self):
        return self.gui.cursor.hide_standard()

    def cursor_top(self):
        return self.gui.cursor.cursor_top()

    @staticmethod
    def set_amb_lgt(col):
        return ShaderMgr().set_amb_lgt(col)

    @staticmethod
    def set_dir_lgt(col, hpr):
        return ShaderMgr().set_dir_lgt(col, hpr)

    def clear_lights(self):
        return self.shader_mgr.clear_lights()

    def toggle_shader(self):
        return self.shader_mgr.toggle_shader()

    @property
    def cfg(self):
        return self.logic.cfg

    @property
    def is_runtime(self):
        return self.logic.is_runtime

    @property
    def languages(self):
        return self.logic.cfg.languages

    @property
    def resolutions(self):
        return self.gui.resolutions

    @property
    def closest_res(self):
        return self.gui.closest_res

    def set_resolution(self, res):
        return self.gui.set_resolution(res)

    def toggle_fullscreen(self):
        return self.gui.toggle_fullscreen()
