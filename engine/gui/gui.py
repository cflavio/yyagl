from panda3d.core import WindowProperties
from ...gameobject import Gui
from ..log import LogMgr
from .cursor import MouseCursor
from .browser import Browser


class EngineGuiBase(Gui):

    @staticmethod
    def init_cls():
        return EngineGui if eng.base.win else EngineGuiBase

    def __init__(self, mdt):
        Gui.__init__(self, mdt)
        eng.base.disableMouse()
        self.browser = Browser.init_cls()

    def open_browser(self, url):
        self.browser.open(url)

    @property
    def resolutions(self):
        d_i = eng.base.pipe.getDisplayInformation()

        def res(idx):
            return d_i.getDisplayModeWidth(idx), d_i.getDisplayModeHeight(idx)

        res_values = [res(idx) for idx in range(d_i.getTotalDisplayModes())]
        return sorted(list(set(res_values)))

    @property
    def resolution(self):
        win_prop = eng.base.win.get_properties()
        return win_prop.get_x_size(), win_prop.get_y_size()

    @property
    def closest_res(self):
        def distance(res):
            curr_res = self.resolution
            return abs(res[0] - curr_res[0]) + abs(res[1] - curr_res[1])

        dist_lst = map(distance, self.resolutions)
        try:
            idx_min = dist_lst.index(min(dist_lst))
            return self.resolutions[idx_min]
        except ValueError:  # sometimes we have empty resolutions
            return self.resolution

    def set_resolution_check(self, res):
        res_msg = 'resolutions: {curr} (current), {res} (wanted)'
        LogMgr().log(res_msg.format(curr=self.resolution, res=res))
        if self.resolution != res:
            retry = 'second attempt: {curr} (current) {res} (wanted)'
            LogMgr().log(retry.format(curr=self.resolution, res=res))
            self.set_resolution(res, False)

    def toggle_fullscreen(self):
        self.set_resolution(self.closest_res)
        props = WindowProperties()
        props.set_fullscreen(not eng.base.win.is_fullscreen())
        base.win.requestProperties(props)


class EngineGui(EngineGuiBase):

    def __init__(self, mdt):
        EngineGuiBase.__init__(self, mdt)
        cfg = eng.logic.cfg
        resol = cfg.win_size.split()
        self.set_resolution(tuple(int(size) for size in resol), fullscreen=cfg.fullscreen)
        self.cursor = MouseCursor(cfg.cursor_path, cfg.cursor_scale,
                                  cfg.cursor_hotspot)

    def set_resolution(self, res, check=True, fullscreen=None):
        LogMgr().log('setting resolution ' + str(res))
        props = WindowProperties()
        props.set_size(res)
        if fullscreen:
            props.set_fullscreen(True)
        eng.base.win.request_properties(props)
        if check:
            args = 3.0, self.set_resolution_check, 'resolution check', [res]
            taskMgr.doMethodLater(*args)
