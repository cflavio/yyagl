from panda3d.core import WindowProperties
from direct.gui.OnscreenImage import OnscreenImage


class Cursor:

    def __init__(self, path, scale, hotspot):
        if not path:
            return
        props = WindowProperties()
        props.setCursorHidden(True)
        base.win.requestProperties(props)
        self.cursor_img = OnscreenImage(path)
        self.cursor_img.setTransparency(True)
        self.cursor_img.setScale(scale)
        self.cursor_img.setBin('gui-popup', 50)
        self.hotspot_dx = scale[0] * (1 - 2 * hotspot[0])
        self.hotspot_dy = scale[2] * (1 - 2 * hotspot[1])
        eng.event.attach(self.on_frame)

    def show(self):
        self.cursor_img.show()

    def hide(self):
        self.cursor_img.hide()

    def on_frame(self):
        if base.mouseWatcherNode.hasMouse():
            x = base.mouseWatcherNode.getMouseX()
            y = base.mouseWatcherNode.getMouseY()
            h_x = x * base.getAspectRatio() + self.hotspot_dx
            self.cursor_img.setPos(h_x, 0, y - self.hotspot_dy)
