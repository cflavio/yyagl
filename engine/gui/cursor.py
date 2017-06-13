from panda3d.core import WindowProperties
from direct.gui.OnscreenImage import OnscreenImage


class MouseCursor:

    def __init__(self, fpath, scale, hotspot):
        if not fpath:
            return
        self.__set_standard_cursor(False)
        self.cursor_img = OnscreenImage(fpath)
        self.cursor_img.set_transparency(True)
        self.cursor_img.set_scale(scale)
        self.cursor_img.set_bin('gui-popup', 50)
        self.hotspot_dx = scale[0] * (1 - 2 * hotspot[0])
        self.hotspot_dy = scale[2] * (1 - 2 * hotspot[1])
        eng.attach_obs(self.on_frame)

    def __set_standard_cursor(self, show):
        props = WindowProperties()
        props.set_cursor_hidden(not show)
        base.win.requestProperties(props)

    def show(self):
        self.cursor_img.show()

    def show_standard(self):
        self.__set_standard_cursor(True)

    def hide(self):
        self.cursor_img.hide()

    def hide_standard(self):
        self.__set_standard_cursor(False)

    def cursor_top(self):
        self.cursor_img.reparent_to(self.cursor_img.get_parent())

    def on_frame(self):
        if not base.mouseWatcherNode.hasMouse():
            return
        x = base.mouseWatcherNode.get_mouse_x()
        y = base.mouseWatcherNode.get_mouse_y()
        h_x = x * base.getAspectRatio() + self.hotspot_dx
        self.cursor_img.set_pos(h_x, 0, y - self.hotspot_dy)
