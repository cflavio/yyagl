from yyagl.lib.gui import Img
from yyagl.gameobject import GameObject
from yyagl.facade import Facade


class MouseCursorFacade(Facade):

    def __init__(self):
        fwds = [
            ('show', lambda obj: obj.cursor_img.show),
            ('hide', lambda obj: obj.cursor_img.hide)]
        map(lambda args: self._fwd_mth(*args), fwds)


class MouseCursor(GameObject, MouseCursorFacade):

    def __init__(self, filepath, scale, hotspot):
        GameObject.__init__(self)
        MouseCursorFacade.__init__(self)
        self.eng.lib.set_std_cursor(False)
        self.cursor_img = Img(filepath, scale=scale, foreground=True)
        self.hotspot_dx = scale[0] * (1 - 2 * hotspot[0])
        self.hotspot_dy = scale[2] * (1 - 2 * hotspot[1])
        self.eng.attach_obs(self.on_frame)
        if self.eng.lib.version().startswith('1.10'):
            self.eng.attach_obs(self.on_frame_unpausable)

    def show_standard(self): self.eng.lib.set_std_cursor(True)

    def hide_standard(self): self.eng.lib.set_std_cursor(False)

    def cursor_top(self):
        self.cursor_img.reparent_to(self.cursor_img.parent)

    def __on_frame(self):
        mouse = self.eng.lib.get_mouse()
        if not mouse: return
        h_x = mouse[0] * self.eng.lib.aspect_ratio() + self.hotspot_dx
        self.cursor_img.set_pos((h_x, mouse[1] - self.hotspot_dy))

    def on_frame(self):
        if not self.eng.pause.is_paused: self.__on_frame()

    def on_frame_unpausable(self):
        if self.eng.pause.is_paused: self.__on_frame()
