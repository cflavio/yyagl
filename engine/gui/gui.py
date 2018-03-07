from panda3d.core import WindowProperties
from ...gameobject import GuiColleague
from .cursor import MouseCursor
from .browser import Browser


class EngineGuiBase(GuiColleague):

    @staticmethod
    def init_cls():
        return EngineGui if GuiColleague.eng.lib.has_window() else EngineGuiBase

    @staticmethod
    def open_browser(url): Browser.open(url)

    @property
    def resolutions(self):
        return sorted(list(set(self.eng.lib.resolutions)))

    @property
    def closest_resolution(self):
        def distance(res):
            curr_res = self.eng.lib.resolution
            return abs(res[0] - curr_res[0]) + abs(res[1] - curr_res[1])

        try:
            return min(self.resolutions, key=distance)
        except ValueError:  # sometimes we have empty resolutions
            return self.resolution

    def set_resolution_check(self, res):
        res_msg = 'resolutions: {curr} (current), {res} (wanted)'
        self.eng.log(res_msg.format(curr=self.eng.lib.resolution, res=res))
        if self.eng.lib.resolution == res: return
        retry = 'second attempt: {curr} (current) {res} (wanted)'
        self.eng.log(retry.format(curr=self.eng.lib.resolution, res=res))
        self.set_resolution(res, False)

    def toggle_fullscreen(self):
        self.set_resolution(self.closest_resolution)
        self.eng.lib.toggle_fullscreen()


class EngineGui(EngineGuiBase):

    def __init__(self, mediator):
        EngineGuiBase.__init__(self, mediator)
        cfg = self.eng.cfg
        resol = cfg.gui_cfg.win_size.split()
        res = tuple(int(size) for size in resol)
        self.set_resolution(res, fullscreen=cfg.gui_cfg.fullscreen)
        cur_cfg = cfg.cursor_cfg
        self.cursor = MouseCursor(
            cur_cfg.cursor_path, cur_cfg.cursor_scale, cur_cfg.cursor_hotspot)

    def set_resolution(self, res, check=True, fullscreen=None):
        self.eng.log('setting resolution ' + str(res))
        self.eng.lib.set_resolution(res, fullscreen)
        if check: self.eng.do_later(3.0, self.set_resolution_check, [res])
