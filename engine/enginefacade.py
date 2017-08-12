from .shader import ShaderMgr
from .font import FontMgr
from ..facade import Facade


class EngineFacade(Facade):

    def __init__(self):
        # lambdas are for lazy evaluation (they may not exist)
        fwd = self._fwd_mth_lazy
        fwd('attach_obs', lambda: self.event.attach)
        fwd('detach_obs', lambda: self.event.detach)
        fwd('attach_node', lambda: self.gfx.root.attachNewNode)
        fwd('particle', lambda: self.gfx.particle)
        fwd('init_gfx', lambda: self.gfx.init)
        fwd('clean_gfx', lambda: self.gfx.clean)
        fwd('set_cam_pos', lambda: self.base.camera.set_pos)
        fwd('load_font', lambda: FontMgr().load_font)
        fwd('open_browser', lambda: self.gui.open_browser)
        fwd('toggle_pause', lambda: self.pause.logic.toggle)
        fwd('play', lambda: self.audio.play)
        fwd('set_volume', lambda: self.audio.set_volume)
        fwd('show_cursor', lambda: self.gui.cursor.show)
        fwd('show_standard_cursor', lambda: self.gui.cursor.show_standard)
        fwd('hide_cursor', lambda: self.gui.cursor.hide)
        fwd('hide_standard_cursor', lambda: self.gui.cursor.hide_standard)
        fwd('cursor_top', lambda: self.gui.cursor.cursor_top)
        fwd('set_amb_lgt', lambda: ShaderMgr().set_amb_lgt)
        fwd('set_dir_lgt', lambda: ShaderMgr().set_dir_lgt)
        fwd('clear_lights', lambda: self.shader_mgr.clear_lights)
        fwd('toggle_shader', lambda: self.shader_mgr.toggle_shader)
        fwd('set_resolution', lambda: self.gui.set_resolution)
        fwd('toggle_fullscreen', lambda: self.gui.toggle_fullscreen)
        fwd('norm_vec', lambda: self.logic.norm_vec)
        self._fwd_prop_lazy('version', lambda: self.logic.version)
        self._fwd_prop_lazy('curr_path', lambda: self.logic.curr_path)
        self._fwd_prop_lazy('cfg', lambda: self.logic.cfg)
        self._fwd_prop_lazy('is_runtime', lambda: self.logic.is_runtime)
        self._fwd_prop_lazy('languages', lambda: self.logic.cfg.languages)
        self._fwd_prop_lazy('resolutions', lambda: self.gui.resolutions)
        self._fwd_prop_lazy('closest_res', lambda: self.gui.closest_res)

    @staticmethod
    def do_later(time, meth, args=[]):
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
