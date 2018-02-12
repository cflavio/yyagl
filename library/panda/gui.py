from direct.gui.DirectButton import DirectButton
from direct.gui.OnscreenImage import OnscreenImage
from direct.gui.DirectSlider import DirectSlider
from ..igui import IImg, IBtn


class PandaImg(IImg):

    def __init__(self, fpath, scale=1.0, is_background=False):
        self.img = OnscreenImage(fpath, scale=scale)
        if is_background: self.img.set_bin('background', 10)

    def destroy(self):
        self.img = self.img.destroy()


class PandaBtn(IBtn):

    def __init__(
            self, text='', parent=None, pos=(0, 0, 0), scale=(1, 1, 1),
            command=None, frameSize=(-1, 1, -1, 1), clickSound=None,
            text_fg=(1, 1, 1, 1), frameColor=(1, 1, 1, 1), text_font=None,
            rolloverSound=None, extraArgs=[], frameTexture=None, image=None,
            text_scale=1.0):
        self.btn = DirectButton(
            text=text, parent=parent, pos=pos, scale=scale, command=command,
            frameSize=frameSize, clickSound=clickSound, text_fg=text_fg,
            frameColor=frameColor, text_font=text_font,
            rolloverSound=rolloverSound, extraArgs=extraArgs,
            frameTexture=frameTexture, image=image, text_scale=1.0)

    def initialiseoptions(self, cls): return self.btn.initialiseoptions(cls)

    def get_np(self): return self.btn

    def __setitem__(self, key, value): self.btn[key] = value

    def __getitem__(self, key): return self.btn[key]

    def get_pos(self, pos=None):
        return self.btn.get_pos(*[pos] if pos else [])

    def set_pos(self, pos): return self.btn.set_pos(pos)

    def set_z(self, z): return self.btn.set_z(z)

    def set_shader(self, shader): return self.btn.set_shader(shader)

    def set_shader_input(self, input_name, input_val):
        return self.btn.set_shader_input(input_name, input_val)

    def set_transparency(self, val): return self.btn.set_transparency(val)

    def bind(self, evt, callback):
        return self.btn.bind(evt, callback)

    def attachNewNode(self, gui_itm, sort_order):
        return self.btn.attachNewNode(gui_itm, sort_order)

    def show(self): return self.btn.show()

    def hide(self): return self.btn.hide()

    def is_hidden(self): return self.btn.is_hidden()

    def destroy(self): return self.btn.destroy()


class PandaSlider(IBtn):

    def __init__(
            self, parent=None, pos=(0, 0, 0), scale=1, value=0, frameColor=(1, 1, 1, 1),
            thumb_frameColor=(1, 1, 1, 1), command=None, range=(0, 1)):
        self.slider = DirectSlider(parent=parent, pos=pos, scale=scale,
            value=value, frameColor=frameColor,
            thumb_frameColor=thumb_frameColor, command=command, range=range)

    def get_np(self): return self.slider

    def get_pos(self, pos=None):
        return self.slider.get_pos(*[pos] if pos else [])

    def set_pos(self, pos): return self.slider.set_pos(pos)

    def __setitem__(self, key, value): self.slider[key] = value

    def __getitem__(self, key): return self.slider[key]

    def show(self): return self.slider.show()

    def hide(self): return self.slider.hide()

    def is_hidden(self): return self.slider.is_hidden()

    def get_value(self): return self.slider.getValue()

    def destroy(self): return self.slider.destroy()
