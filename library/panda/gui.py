from panda3d.core import TextNode, Texture
from direct.gui.DirectGuiGlobals import FLAT, ENTER, EXIT, DISABLED, NORMAL, \
    B1PRESS
from direct.showbase.DirectObject import DirectObject
from direct.gui.DirectButton import DirectButton
from direct.gui.DirectCheckButton import DirectCheckButton
from direct.gui.DirectOptionMenu import DirectOptionMenu
from direct.gui.OnscreenImage import OnscreenImage
from direct.gui.DirectSlider import DirectSlider
from direct.gui.DirectEntry import DirectEntry
from direct.gui.DirectLabel import DirectLabel
from direct.gui.DirectFrame import DirectFrame
from direct.gui.OnscreenText import OnscreenText
from ..igui import IImg, IBtn, ICheckBtn, IOptionMenu, IEntry, ILabel, IText, \
    IFrame


class PandaImg(IImg):

    def __init__(self, fpath, pos=(0, 1, 0), scale=1.0, is_background=False,
                 force_transp=None, layer='', parent=None):
        self.img = OnscreenImage(fpath, pos=pos, scale=scale, parent=parent)
        if is_background: self.img.set_bin('background', 10)
        if force_transp: self.img.set_transparency(True)
        elif force_transp is None:
            alpha_formats = [12]  # panda3d.core.texture.Frgba
            if self.img.get_texture().get_format() in alpha_formats:
                self.img.set_transparency(True)
        if layer == 'fg': self.img.set_bin('gui-popup', 50)

    def set_pos(self, pos): return self.img.set_pos(pos)

    def get_pos(self, pos=None):
        return self.img.get_pos(*[pos] if pos else [])

    def reparent_to(self, parent): return self.img.reparent_to(parent)

    def get_parent(self): return self.img.get_parent()

    def show(self): return self.img.show()

    def hide(self): return self.img.hide()

    def is_hidden(self): return self.img.is_hidden()

    def set_shader(self, shader): return self.img.set_shader(shader)

    def set_shader_input(self, input_name, input_val):
        return self.img.set_shader_input(input_name, input_val)

    def set_transparency(self, val): return self.img.set_transparency(val)

    def set_texture(self, tstage, tex): return self.img.set_texture(tstage, tex)

    def destroy(self): self.img = self.img.destroy()


class PandaBase(object):

    def __init__(self, tra_src=None, tra_tra=None):
        if tra_src and tra_tra: self.bind_tra(tra_src, tra_tra)

    def bind_tra(self, text_src, text_transl):
        # text_transl is not used, anyway we need it since we have this kind of
        # use: self.bind_transl('example str', _('example str'))
        # this allows to change translations on the fly keeping the source
        # text for remapping it later
        self.text_src_tra = text_src
        self.__class__.bind_transl = property(lambda self: _(self.text_src_tra))
        self['text'] = self.bind_transl

    def get_pos(self, pos=None):
        return self.wdg.get_pos(*[pos] if pos else [])

    def set_pos(self, pos): return self.wdg.set_pos(pos)

    def __setitem__(self, key, value): self.wdg[key] = value

    def __getitem__(self, key): return self.wdg[key]

    def get_np(self): return self.wdg

    def show(self): return self.wdg.show()

    def hide(self): return self.wdg.hide()

    def is_hidden(self): return self.wdg.is_hidden()

    def destroy(self): return self.wdg.destroy()


class PandaAbs(PandaBase):

    def get_value(self): return self.wdg.getValue()

    def initialiseoptions(self, cls): return self.wdg.initialiseoptions(cls)

    def set_z(self, z): return self.wdg.set_z(z)

    def set_shader(self, shader): return self.wdg.set_shader(shader)

    def set_shader_input(self, input_name, input_val):
        return self.wdg.set_shader_input(input_name, input_val)

    def set_transparency(self, val): return self.wdg.set_transparency(val)

    def bind(self, evt, callback):
        return self.wdg.bind(evt, callback)

    def attachNewNode(self, gui_itm, sort_order):
        # it won't work if we name it attach_node. hopefully this will be
        # possible when we'll use decorators in place of mixins
        return self.wdg.attachNewNode(gui_itm, sort_order)

    @property
    def is_enabled(self): return self.wdg['state'] != DISABLED


class PandaBtn(IBtn, PandaAbs):

    def __init__(
            self, text='', parent=None, pos=(0, 0, 0), scale=(1, 1, 1),
            command=None, frameSize=(-1, 1, -1, 1), clickSound=None,
            text_fg=(1, 1, 1, 1), frameColor=(1, 1, 1, 1), text_font=None,
            rolloverSound=None, extraArgs=[], frameTexture=None, image=None,
            tra_src=None, tra_tra=None):
        self.wdg = DirectButton(
            text=text, parent=parent, pos=pos, scale=scale, command=command,
            frameSize=frameSize, clickSound=clickSound, text_fg=text_fg,
            frameColor=frameColor, text_font=text_font,
            rolloverSound=rolloverSound, extraArgs=extraArgs,
            frameTexture=frameTexture, image=image, text_scale=1.0)
        PandaAbs.__init__(self, tra_src, tra_tra)
        self['relief'] = FLAT
        self.bind(ENTER, self._on_enter)
        self.bind(EXIT, self._on_exit)

    def _on_enter(self, pos): pass  # pos comes from mouse

    def _on_exit(self, pos): pass  # pos comes from mouse

    def enable(self):
        self['state'] = NORMAL

    def disable(self):
        self['state'] = DISABLED


class PandaSlider(IBtn, PandaAbs):

    def __init__(
            self, parent=None, pos=(0, 0, 0), scale=1, value=0,
            frameColor=(1, 1, 1, 1), thumb_frameColor=(1, 1, 1, 1),
            command=None, range_=(0, 1), tra_src=None, tra_tra=None):
        self.wdg = DirectSlider(
            parent=parent, pos=pos, scale=scale, value=value,
            frameColor=frameColor, thumb_frameColor=thumb_frameColor,
            command=command, range=range_)
        PandaAbs.__init__(self, tra_src, tra_tra)


class PandaCheckBtn(ICheckBtn, PandaAbs):

    def __init__(
            self, pos=(0, 1, 0), text='', indicatorValue=False,
            indicator_frameColor=(1, 1, 1, 1), frameColor=(1, 1, 1, 1),
            scale=(1, 1, 1), clickSound=None, rolloverSound=None,
            text_fg=(1, 1, 1, 1), text_font=None, command=None, tra_src=None,
            tra_tra=None):
        self.wdg = DirectCheckButton(
            pos=pos, text=text, indicatorValue=indicatorValue,
            indicator_frameColor=indicator_frameColor,
            frameColor=frameColor, scale=scale, clickSound=clickSound,
            rolloverSound=rolloverSound, text_fg=text_fg, text_font=text_font,
            command=command)
        PandaAbs.__init__(self, tra_src, tra_tra)


class PandaOptionMenu(IOptionMenu, PandaAbs):

    def __init__(
            self, text='', items=[], pos=(0, 1, 0), scale=(1, 1, 1),
            initialitem='', command=None, frameSize=(-1, 1, -1, 1),
            clickSound=None, rolloverSound=None, textMayChange=False,
            text_fg=(1, 1, 1, 1), item_frameColor=(1, 1, 1, 1),
            frameColor=(1, 1, 1, 1), highlightColor=(1, 1, 1, 1),
            text_scale=.05, popupMarker_frameColor=(1, 1, 1, 1),
            item_relief=None, item_text_font=None, text_font=None, tra_src=None,
            tra_tra=None):
        self.wdg = DirectOptionMenu(
            text=text, items=items, pos=pos, scale=scale,
            initialitem=initialitem, command=command, frameSize=frameSize,
            clickSound=clickSound, rolloverSound=rolloverSound,
            textMayChange=textMayChange, text_fg=text_fg,
            item_frameColor=item_frameColor, frameColor=frameColor,
            highlightColor=highlightColor, text_scale=text_scale,
            popupMarker_frameColor=popupMarker_frameColor,
            item_relief=item_relief, item_text_font=item_text_font,
            text_font=text_font)
        PandaAbs.__init__(self, tra_src, tra_tra)

    def set(self, val, f_cmd=None): return self.wdg.set(val, f_cmd)

    def get(self): return self.wdg.get()

    @property
    def selected_idx(self): return self.wdg.selectedIndex


class PandaEntry(IEntry, PandaAbs, DirectObject):

    def __init__(
            self, scale=.05, pos=(0, 1, 0), entryFont=None, width=12,
            frameColor=(1, 1, 1, 1), initialText='', obscured=False,
            command=None, focusInCommand=None, focusInExtraArgs=[],
            focusOutCommand=None, focusOutExtraArgs=[], parent=None,
            tra_src=None, tra_tra=None, text_fg=(1, 1, 1, 1), on_tab=None,
            on_click=None):
        DirectObject.__init__(self)
        self.wdg = DirectEntry(
            scale=scale, pos=pos, entryFont=entryFont, width=width,
            frameColor=frameColor, initialText=initialText, obscured=obscured,
            command=command, focusInCommand=focusInCommand,
            focusInExtraArgs=focusInExtraArgs, focusOutCommand=focusOutCommand,
            focusOutExtraArgs=focusOutExtraArgs, parent=parent,
            text_fg=text_fg)
        PandaAbs.__init__(self, tra_src, tra_tra)
        if on_tab:
            self.on_tab_cb = on_tab
            self.accept('tab-up', self.on_tab)
        if on_click: self.wdg.bind(B1PRESS, on_click)

    def on_tab(self):
        if self.wdg['focus']: self.on_tab_cb()

    def get(self): return self.wdg.get()

    def set(self, txt): return self.wdg.set(txt)

    def enter_text(self, txt): return self.wdg.enterText(txt)

    def enable(self):
        self['state'] = NORMAL

    def disable(self):
        self['state'] = DISABLED

    def destroy(self):
        self.ignore('tab-up')
        self.on_tab_cb = None
        PandaAbs.destroy(self)


class PandaLabel(ILabel, PandaAbs):

    def __init__(
            self, text='', pos=(0, 1, 0), parent=None, text_wordwrap=10,
            text_align=None, text_fg=(1, 1, 1, 1), text_font=None, scale=.05,
            frameColor=(1, 1, 1, 1), tra_src=None, tra_tra=None):
        self.wdg = DirectLabel(
            text=text, pos=pos, parent=parent, text_wordwrap=text_wordwrap,
            text_align=text_align, text_fg=text_fg, text_font=text_font,
            scale=scale, frameColor=frameColor)
        PandaAbs.__init__(self, tra_src, tra_tra)


class PandaTxt(IText, PandaBase):

    def __init__(
            self, txt='', pos=(0, 1, 0), scale=.05, wordwrap=12, parent=None,
            fg=(1, 1, 1, 1), font=None, align=None, tra_src=None,
            tra_tra=None):
        str2par = {'bottomleft': base.a2dBottomLeft,
                   'leftcenter': base.a2dLeftCenter}
        str2al = {'left': TextNode.A_left, 'right': TextNode.A_right}
        if parent: parent = str2par[parent]
        if align: align = str2al[align]
        self.wdg = OnscreenText(
            text=txt, pos=pos, scale=scale, wordwrap=wordwrap,
            parent=parent, fg=fg, font=font, align=align)
        PandaBase.__init__(self, tra_src, tra_tra)

    def set_r(self, val): return self.wdg.set_r(val)


class PandaFrame(IFrame, PandaAbs):

    def __init__(self, frameSize=(-1, 1, -1, 1), frameColor=(1, 1, 1, 1),
                 pos=(0, 1, 0), parent=None, textureCoord=False):
        PandaAbs.__init__(self)
        self.wdg = DirectFrame(frameSize=frameSize, frameColor=frameColor,
                               pos=pos, parent=parent)
        if textureCoord:
            self.wdg['frameTexture'] = Texture()
