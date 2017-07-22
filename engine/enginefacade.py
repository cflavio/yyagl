from .shader import ShaderMgr
from .font import FontMgr
from ..facade import Facade


class EngineFacade(Facade):

    def __init__(self):
        # lambdas are for lazy evaluation (they may not exist)
        self._fwd_mth_lazy('attach_obs', lambda: self.event.attach)
        self._fwd_mth_lazy('detach_obs', lambda: self.event.detach)
        self._fwd_mth_lazy('attach_node', lambda: self.gfx.root.attachNewNode)
        self._fwd_mth_lazy('particle', lambda: self.gfx.particle)
        self._fwd_mth_lazy('init_gfx', lambda: self.gfx.init)
        self._fwd_mth_lazy('clean_gfx', lambda: self.gfx.clean)
        self._fwd_mth_lazy('set_cam_pos', lambda: self.base.camera.set_pos)
        self._fwd_mth_lazy('load_font', lambda: FontMgr().load_font)
        self._fwd_mth_lazy('open_browser', lambda: self.gui.open_browser)
        self._fwd_mth_lazy('toggle_pause', lambda: self.pause.logic.toggle)
        self._fwd_mth_lazy('play', lambda: self.audio.play)
        self._fwd_mth_lazy('set_volume', lambda: self.audio.set_volume)
        self._fwd_mth_lazy('show_cursor', lambda: self.gui.cursor.show)
        self._fwd_mth_lazy('show_standard_cursor', lambda: self.gui.cursor.show_standard)
        self._fwd_mth_lazy('hide_cursor',lambda:  self.gui.cursor.hide)
        self._fwd_mth_lazy('hide_standard_cursor', lambda: self.gui.cursor.hide_standard)
        self._fwd_mth_lazy('cursor_top', lambda: self.gui.cursor.cursor_top)
        self._fwd_mth_lazy('set_amb_lgt', lambda: ShaderMgr().set_amb_lgt)
        self._fwd_mth_lazy('set_dir_lgt', lambda: ShaderMgr().set_dir_lgt)
        self._fwd_mth_lazy('clear_lights', lambda: self.shader_mgr.clear_lights)
        self._fwd_mth_lazy('toggle_shader', lambda: self.shader_mgr.toggle_shader)
        self._fwd_mth_lazy('set_resolution', lambda: self.gui.set_resolution)
        self._fwd_mth_lazy('toggle_fullscreen', lambda: self.gui.toggle_fullscreen)
        self._fwd_prop_lazy('version', lambda: self.logic.version)
        self._fwd_prop_lazy('curr_path', lambda: self.logic.curr_path)
        self._fwd_prop_lazy('cfg', lambda: self.logic.cfg)
        self._fwd_prop_lazy('is_runtime', lambda: self.logic.is_runtime)
        self._fwd_prop_lazy('languages', lambda: self.logic.cfg.languages)
        self._fwd_prop_lazy('resolutions', lambda: self.gui.resolutions)
        self._fwd_prop_lazy('closest_res', lambda: self.gui.closest_res)

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
