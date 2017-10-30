from panda3d.core import WindowProperties
from direct.gui.OnscreenImage import OnscreenImage
from yyagl.gameobject import GameObject


class MouseCursor(GameObject):

    def __init__(self, fpath, scale, hotspot):
        if not fpath: return
        GameObject.__init__(self)
        self.__set_standard_cursor(False)
        self.cursor_img = OnscreenImage(fpath)
        self.cursor_img.set_transparency(True)
        self.cursor_img.set_scale(scale)
        self.cursor_img.set_bin('gui-popup', 50)
        self.hotspot_dx = scale[0] * (1 - 2 * hotspot[0])
        self.hotspot_dy = scale[2] * (1 - 2 * hotspot[1])
        self.eng.attach_obs(self.on_frame_unpausable)

    @staticmethod
    def __set_standard_cursor(show):
        props = WindowProperties()
        props.set_cursor_hidden(not show)
        base.win.requestProperties(props)

    def show(self): self.cursor_img.show()

    def show_standard(self): self.__set_standard_cursor(True)

    def hide(self): self.cursor_img.hide()

    def hide_standard(self): self.__set_standard_cursor(False)

    def cursor_top(self):
        self.cursor_img.reparent_to(self.cursor_img.get_parent())

    def on_frame_unpausable(self):
        if not base.mouseWatcherNode.hasMouse(): return
        m_x = base.mouseWatcherNode.get_mouse_x()
        m_y = base.mouseWatcherNode.get_mouse_y()
        h_x = m_x * base.getAspectRatio() + self.hotspot_dx
        self.cursor_img.set_pos(h_x, 0, m_y - self.hotspot_dy)
