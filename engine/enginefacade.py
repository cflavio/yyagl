from ..facade import Facade


class EngineFacade(Facade):

    def __init__(self):
        # lambdas are for lazy evaluation (they may not exist)
        fwd = self._fwd_mth
        fwd('attach_obs', lambda obj: obj.event.attach)
        fwd('detach_obs', lambda obj: obj.event.detach)
        fwd('attach_node', lambda obj: obj.gfx.root.attach_node)
        fwd('particle', lambda obj: obj.gfx.particle)
        fwd('init_gfx', lambda obj: obj.gfx.init)
        fwd('clean_gfx', lambda obj: obj.gfx.clean)
        fwd('set_cam_pos', lambda obj: base.camera.set_pos)
        fwd('load_font', lambda obj: self.eng.font_mgr.load_font)
        fwd('open_browser', lambda obj: obj.gui.open_browser)
        fwd('toggle_pause', lambda obj: obj.pause.logic.toggle)
        fwd('play', lambda obj: obj.audio.play)
        fwd('set_volume', lambda obj: obj.audio.set_volume)
        fwd('show_cursor', lambda obj: obj.gui.cursor.show)
        fwd('show_standard_cursor', lambda obj: obj.gui.cursor.show_standard)
        fwd('hide_cursor', lambda obj: obj.gui.cursor.hide)
        fwd('hide_standard_cursor', lambda obj: obj.gui.cursor.hide_standard)
        fwd('cursor_top', lambda obj: obj.gui.cursor.cursor_top)
        fwd('set_amb_lgt', lambda obj: obj.shader_mgr.set_amb_lgt)
        fwd('set_dir_lgt', lambda obj: obj.shader_mgr.set_dir_lgt)
        fwd('clear_lights', lambda obj: obj.shader_mgr.clear_lights)
        fwd('toggle_shader', lambda obj: obj.shader_mgr.toggle_shader)
        fwd('set_resolution', lambda obj: obj.gui.set_resolution)
        fwd('toggle_fullscreen', lambda obj: obj.gui.toggle_fullscreen)
        fwd('send', lambda obj: obj.lib.send)
        fwd('do_later', lambda obj: obj.lib.do_later)
        fwd('add_task', lambda obj: obj.lib.add_task)
        self._fwd_prop('version', lambda obj: obj.logic.version)
        self._fwd_prop('curr_path', lambda obj: obj.logic.curr_path)
        self._fwd_prop('cfg', lambda obj: obj.logic.cfg)
        self._fwd_prop('is_runtime', lambda obj: obj.logic.is_runtime)
        self._fwd_prop('languages', lambda obj: obj.logic.cfg.lang_cfg.languages)
        self._fwd_prop('resolutions', lambda obj: obj.gui.resolutions)
        self._fwd_prop('closest_res', lambda obj: obj.gui.closest_res)
        self._fwd_prop('joystick_mgr', lambda obj: obj.event.joystick_mgr)
        self._fwd_prop('curr_time',
                            lambda obj: globalClock.get_frame_time())

    def remove_do_later(self, tsk):
        self.pause.remove_task(tsk)
        return self.lib.remove_task(tsk)

    def load_model(self, filename, callback=None, extra_args=[], anim=None):
        return self.gfx.load_model(filename, callback, extra_args, anim)
