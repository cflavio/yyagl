from yyagl.facade import Facade


class EngineFacade(Facade):

    def __init__(self):
        # lambdas are for lazy evaluation (they may not exist)
        prop_lst = [
            ('version', lambda obj: obj.logic.version),
            ('curr_path', lambda obj: obj.logic.curr_path),
            ('cfg', lambda obj: obj.logic.cfg),
            ('is_runtime', lambda obj: obj.logic.is_runtime),
            ('languages', lambda obj: obj.logic.cfg.lang_cfg.languages),
            ('resolutions', lambda obj: obj.gui.resolutions),
            ('closest_resolution', lambda obj: obj.gui.closest_resolution),
            ('joystick_mgr', lambda obj: obj.event.joystick_mgr),
            ('curr_time', lambda obj: self.clock.time)]
        mth_lst = [
            ('attach_obs', lambda obj: obj.event.attach),
            ('detach_obs', lambda obj: obj.event.detach),
            ('attach_node', lambda obj: obj.gfx.root.attach_node),
            ('particle', lambda obj: obj.gfx.particle),
            ('init_gfx', lambda obj: obj.gfx.init),
            ('clean_gfx', lambda obj: obj.gfx.clean),
            ('set_cam_pos', lambda obj: base.camera.set_pos),
            ('load_font', lambda obj: self.eng.font_mgr.load_font),
            ('open_browser', lambda obj: obj.gui.open_browser),
            ('toggle_pause', lambda obj: obj.pause.logic.toggle),
            ('play', lambda obj: obj.audio.play),
            ('set_volume', lambda obj: obj.audio.set_volume),
            ('show_cursor', lambda obj: obj.gui.cursor.show),
            ('show_standard_cursor', lambda obj: obj.gui.cursor.show_standard),
            ('hide_cursor', lambda obj: obj.gui.cursor.hide),
            ('hide_standard_cursor', lambda obj: obj.gui.cursor.hide_standard),
            ('cursor_top', lambda obj: obj.gui.cursor.cursor_top),
            ('set_amb_lgt', lambda obj: obj.shader_mgr.set_amb_lgt),
            ('set_dir_lgt', lambda obj: obj.shader_mgr.set_dir_lgt),
            ('clear_lights', lambda obj: obj.shader_mgr.clear_lights),
            ('toggle_shader', lambda obj: obj.shader_mgr.toggle_shader),
            ('set_resolution', lambda obj: obj.gui.set_resolution),
            ('toggle_fullscreen', lambda obj: obj.gui.toggle_fullscreen),
            ('send', lambda obj: obj.lib.send),
            ('do_later', lambda obj: obj.lib.do_later),
            ('add_task', lambda obj: obj.lib.add_task),
            ('remove_task', lambda obj: obj.lib.remove_task),
            ('log', lambda obj: obj.log_mgr.log),
            ('log_tasks', lambda obj: obj.log_mgr.log_tasks)]
        Facade.__init__(self, prop_lst, mth_lst)

    def rm_do_later(self, tsk):
        self.pause.remove_task(tsk)
        return self.lib.remove_task(tsk)

    def load_model(self, filename, callback=None, anim=None):
        return self.gfx.load_model(filename, callback, anim)
