from math import pi


class EngineFacade:

    @property
    def version(self): return self.logic.version

    @property
    def curr_path(self): return self.logic.curr_path

    @property
    def cfg(self): return self.logic.cfg

    @property
    def is_runtime(self): return self.logic.is_runtime

    @property
    def languages(self): return self.logic.cfg.lang_cfg.languages

    @property
    def resolutions(self): return self.gui.resolutions

    @property
    def closest_resolution(self): return self.gui.closest_resolution

    @property
    def joystick_mgr(self): return self.event.joystick_mgr

    @property
    def curr_time(self): return self.clock.time

    def attach_obs(self, obs_meth, sort=10, rename='', args=None):
        args = args or []
        return self.event.attach(obs_meth, sort, rename, args)

    def detach_obs(self, obs_meth, lambda_call=None):
        return self.event.detach(obs_meth, lambda_call)
    def attach_node(self, name): return self.gfx.root.attach_node(name)
    def particle(
            self, parent, texture, color=(1, 1, 1, 1), ampl=pi/6, ray=.5,
            rate=.0001, gravity=-.85, vel=3.8, part_duration=1.0,
            autodestroy=None):
        return self.gfx.particle(
            parent, texture, color, ampl, ray, rate, gravity, vel,
            part_duration, autodestroy)
    def init_gfx(self): return self.gfx.init()
    def clean_gfx(self): return self.gfx.clean()

    @staticmethod
    def set_cam_pos(pos): return base.camera.set_pos(pos)

    def load_font(self, fpath, outline=True):
        return self.eng.font_mgr.load_font(fpath, outline)
    def open_browser(self, url): return self.gui.open_browser(url)

    def toggle_pause(self, show_frm=True):
        return self.pause.logic.toggle(show_frm)

    def play(self): return self.audio.play()
    def set_volume(self, vol): return self.audio.set_volume(vol)
    def show_cursor(self): return self.gui.cursor.show()
    def show_standard_cursor(self): return self.gui.cursor.show_standard()
    def hide_cursor(self): return self.gui.cursor.hide()
    def hide_standard_cursor(self): return self.gui.cursor.hide_standard()
    def cursor_top(self): return self.gui.cursor.cursor_top()
    def set_amb_lgt(self, col): return self.shader_mgr.set_amb_lgt(col)

    def set_dir_lgt(self, col, direction):
        return self.shader_mgr.set_dir_lgt(col, direction)

    def clear_lights(self): return self.shader_mgr.clear_lights()
    def toggle_shader(self): return self.shader_mgr.toggle_shader()

    def set_resolution(self, res, fullscreen=None):
        return self.gui.set_resolution(res, fullscreen)

    def toggle_fullscreen(self): return self.gui.toggle_fullscreen()
    def send(self, msg): return self.lib.send(msg)

    def do_later(self, time, meth, args=None):
        return self.lib.do_later(time, meth, args)

    def add_task(self, mth, priority=0):
        return self.lib.add_task(mth, priority)

    def remove_task(self, tsk): return self.lib.remove_task(tsk)
    def log(self, msg, verbose=False): return self.log_mgr.log(msg, verbose)
    def log_tasks(self): return self.log_mgr.log_tasks()

    def rm_do_later(self, tsk):
        self.pause.remove_task(tsk)
        return self.lib.remove_task(tsk)

    def load_model(self, filename, callback=None, anim=None):
        return self.gfx.load_model(filename, callback, anim)
