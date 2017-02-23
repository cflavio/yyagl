from panda3d.core import WindowProperties
from direct.gui.OnscreenImage import OnscreenImage


class Cursor:

    def __init__(self):
        props = WindowProperties()
        props.setCursorHidden(True)
        base.win.requestProperties(props)
        self.cursor_img = OnscreenImage('assets/images/gui/cursor.png')
        self.cursor_img.setTransparency(True)
        scale = ((256/352.0) * .08, 1, .08)
        hotspot = (.1, .06)
        self.cursor_img.setScale(scale)
        self.cursor_img.setBin('gui-popup', 50)
        self.hotspot_dx = scale[0] * (1 - 2 * hotspot[0])
        self.hotspot_dy = scale[2] * (1 - 2 * hotspot[1])
        taskMgr.add(self._on_frame, '_on_frame')

    def show(self):
        self.cursor_img.show()

    def hide(self):
        self.cursor_img.hide()

    def _on_frame(self, task):
        if base.mouseWatcherNode.hasMouse():
            x = base.mouseWatcherNode.getMouseX()
            y = base.mouseWatcherNode.getMouseY()
            h_x = x * base.getAspectRatio() + self.hotspot_dx
            self.cursor_img.setPos(h_x, 0, y - self.hotspot_dy)
        return task.cont
