from yyagl.lib.gui import Img
from yyagl.gameobject import GameObject
from yyagl.facade import Facade


class MouseCursorFacade(Facade):

    def __init__(self):
        mth_lst = [
            ('show', lambda obj: obj.cursor_img.show),
            ('hide', lambda obj: obj.cursor_img.hide)]
        Facade.__init__(self, mth_lst=mth_lst)


class MouseCursor(GameObject, MouseCursorFacade):

    def __init__(self, filepath, scale, hotspot):
        GameObject.__init__(self)
        MouseCursorFacade.__init__(self)
        if not filepath: return
        self.eng.lib.hide_std_cursor()
        self.cursor_img = Img(filepath, scale=scale, foreground=True)
        self.hotspot_dx = scale[0] * (1 - 2 * hotspot[0])
        self.hotspot_dy = scale[2] * (1 - 2 * hotspot[1])
        self.eng.attach_obs(self.on_frame)
        if self.eng.lib.version.startswith('1.10'):
            self.eng.attach_obs(self.on_frame_unpausable)

    def show_standard(self): self.eng.lib.show_std_cursor()

    def hide_standard(self): self.eng.lib.hide_std_cursor()

    def cursor_top(self):
        self.cursor_img.reparent_to(self.cursor_img.parent)

    def __on_frame(self):
        mouse = self.eng.lib.mousepos
        if not mouse: return
        h_x = mouse[0] * self.eng.lib.aspect_ratio + self.hotspot_dx
        self.cursor_img.set_pos((h_x, mouse[1] - self.hotspot_dy))

    def on_frame(self):
        if not self.eng.pause.paused: self.__on_frame()

    def on_frame_unpausable(self):
        if self.eng.pause.paused: self.__on_frame()
