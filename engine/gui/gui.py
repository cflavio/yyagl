from panda3d.core import WindowProperties
from ...gameobject import Gui
from .cursor import MouseCursor
from .browser import Browser


class EngineGuiBase(Gui):

    @staticmethod
    def init_cls():
        return EngineGui if base.win else EngineGuiBase

    def __init__(self, mdt):
        Gui.__init__(self, mdt)
        base.disableMouse()

    @staticmethod
    def open_browser(url):
        Browser.init_cls().open(url)

    @property
    def resolutions(self):
        d_i = base.pipe.get_display_information()

        def res(idx):
            return d_i.get_display_mode_width(idx), \
                d_i.get_display_mode_height(idx)

        res_values = [res(idx) for idx in range(d_i.get_total_display_modes())]
        return sorted(list(set(res_values)))

    @property
    def resolution(self):
        win_prop = base.win.get_properties()
        return win_prop.get_x_size(), win_prop.get_y_size()

    @property
    def closest_res(self):
        def distance(res):
            curr_res = self.resolution
            return abs(res[0] - curr_res[0]) + abs(res[1] - curr_res[1])

        try:
            return min(self.resolutions, key=distance)
        except ValueError:  # sometimes we have empty resolutions
            return self.resolution

    def set_resolution_check(self, res):
        res_msg = 'resolutions: {curr} (current), {res} (wanted)'
        self.eng.log_mgr.log(res_msg.format(curr=self.resolution, res=res))
        if self.resolution != res:
            retry = 'second attempt: {curr} (current) {res} (wanted)'
            self.eng.log_mgr.log(retry.format(curr=self.resolution, res=res))
            self.set_resolution(res, False)

    def toggle_fullscreen(self):
        self.set_resolution(self.closest_res)
        props = WindowProperties()
        props.set_fullscreen(not base.win.is_fullscreen())
        base.win.request_properties(props)


class EngineGui(EngineGuiBase):

    def __init__(self, mdt):
        EngineGuiBase.__init__(self, mdt)
        cfg = self.eng.logic.cfg
        resol = cfg.win_size.split()
        res = tuple(int(size) for size in resol)
        self.set_resolution(res, fullscreen=cfg.fullscreen)
        self.cursor = MouseCursor(cfg.cursor_path, cfg.cursor_scale,
                                  cfg.cursor_hotspot)

    def set_resolution(self, res, check=True, fullscreen=None):
        self.eng.log_mgr.log('setting resolution ' + str(res))
        props = WindowProperties()
        props.set_size(res)
        if fullscreen:
            props.set_fullscreen(True)
        base.win.request_properties(props)
        if check:
            self.eng.do_later(3.0, self.set_resolution_check, [res])
