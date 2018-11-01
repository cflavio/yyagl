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
from yyagl.facade import Facade


class P3dImg(Facade):

    def __init__(self, filepath, pos=(0, 0), scale=1.0, background=False,
                 force_transp=None, foreground=False, parent=None):
        self.img = OnscreenImage(filepath, pos=(pos[0], 1, pos[1]), scale=scale,
                                 parent=parent)
        if background: self.img.set_bin('background', 10)
        alpha_formats = [12]  # panda3d.core.texture.Frgba
        if self.img.get_texture().get_format() in alpha_formats:
            self.img.set_transparency(True)
        if foreground: self.img.set_bin('gui-popup', 50)
        self._fwd_mth('reparent_to', lambda obj: obj.img.reparent_to)
        self._fwd_mth('show', lambda obj: obj.img.show)
        self._fwd_mth('hide', lambda obj: obj.img.hide)
        self._fwd_mth('set_shader', lambda obj: obj.img.set_shader)
        self._fwd_mth('set_shader_input', lambda obj: obj.img.set_shader_input)
        self._fwd_mth('set_texture', lambda obj: obj.img.set_texture)

    def set_pos(self, pos): return self.img.set_pos(pos[0], 1, pos[1])

    def get_pos(self, pos=None): return self.img.get_pos(*[pos] if pos else [])

    @property
    def parent(self): return self.img.get_parent()

    @property
    def hidden(self): return self.img.is_hidden()

    def set_transparent(self): return self.img.set_transparency(True)

    def destroy(self): self.img = self.img.destroy()


class P3dBase(Facade):

    def __init__(self, tra_src=None, tra_tra=None):
        if tra_src and tra_tra: self.bind_tra(tra_src, tra_tra)
        self._fwd_mth('set_pos', lambda obj: obj.wdg.set_pos)
        self._fwd_mth('show', lambda obj: obj.wdg.show)
        self._fwd_mth('hide', lambda obj: obj.wdg.hide)

    def bind_tra(self, text_src, text_transl):
        # text_transl is not used, anyway we need it since we have this kind of
        # use: self.bind_transl('example str', _('example str'))
        # this allows to change translations on the fly keeping the source
        # text for remapping it later
        # TODO: try reverse mapping? i.e. retrieve the src string from the
        # translated one
        self.text_src_tra = text_src
        self.__class__.bind_transl = property(lambda self: _(self.text_src_tra))
        self['text'] = self.bind_transl

    def get_pos(self, pos=None):
        return self.wdg.get_pos(*[pos] if pos else [])

    def __setitem__(self, key, value): self.wdg[key] = value

    def __getitem__(self, key): return self.wdg[key]

    def get_np(self): return self.wdg

    @property
    def hidden(self): return self.wdg.is_hidden()

    def destroy(self): self.wdg = self.wdg.destroy()


class P3dAbs(P3dBase):


    def __init__(self, tra_src=None, tra_tra=None):
        P3dBase.__init__(self, tra_src, tra_tra)
        self._fwd_mth('get_value', lambda obj: obj.wdg.getValue)
        self._fwd_mth('initialiseoptions', lambda obj: obj.wdg.initialiseoptions)
        self._fwd_mth('set_z', lambda obj: obj.wdg.set_z)
        self._fwd_mth('set_shader', lambda obj: obj.wdg.set_shader)
        self._fwd_mth('set_shader_input', lambda obj: obj.wdg.set_shader_input)
        self._fwd_mth('set_transparency', lambda obj: obj.wdg.set_transparency)
        self._fwd_mth('bind', lambda obj: obj.wdg.bind)

    def attachNewNode(self, gui_itm, sort_order):
        # it won't work if we name it attach_node. hopefully this will be
        # possible when we'll use decorators in place of mixins
        return self.wdg.attachNewNode(gui_itm, sort_order)

    @property
    def is_enabled(self): return self.wdg['state'] != DISABLED


class P3dBtn(P3dAbs):

    def __init__(
            self, text='', parent=None, pos=(0, 0), scale=(1, 1),
            cmd=None, frameSize=(-1, 1, -1, 1), click_snd=None,
            text_fg=(1, 1, 1, 1), frame_col=(1, 1, 1, 1), text_font=None,
            over_snd=None, extra_args=[], frame_texture=None, img=None,
            tra_src=None, tra_tra=None, text_scale=.8):
        self.wdg = DirectButton(
            text=text, parent=parent, pos=(pos[0], 1, pos[1]),
            scale=(scale[0], 1, scale[1]), command=cmd,
            frameSize=frameSize, clickSound=click_snd, text_fg=text_fg,
            frameColor=frame_col, text_font=text_font, rolloverSound=over_snd,
            extraArgs=extra_args, frameTexture=frame_texture, image=img,
            text_scale=1.0)
        P3dAbs.__init__(self, tra_src, tra_tra)
        self['relief'] = FLAT
        args = [(ENTER, self._on_enter), (EXIT, self._on_exit)]
        map(lambda args: self.bind(*args), args)

    def _on_enter(self, pos): pass  # pos comes from mouse

    def _on_exit(self, pos): pass  # pos comes from mouse

    def enable(self): self['state'] = NORMAL

    def disable(self): self['state'] = DISABLED


class P3dSlider(P3dAbs):

    def __init__(
            self, parent=None, pos=(0, 0), scale=1, val=0,
            frame_col=(1, 1, 1, 1), thumb_frame_col=(1, 1, 1, 1),
            cmd=None, range_=(0, 1), tra_src=None, tra_tra=None):
        self.wdg = DirectSlider(
            parent=parent, pos=(pos[0], 1, pos[1]), scale=scale, value=val,
            frameColor=frame_col, thumb_frameColor=thumb_frame_col,
            command=cmd, range=range_)
        P3dAbs.__init__(self, tra_src, tra_tra)


class P3dCheckBtn(P3dAbs):

    def __init__(
            self, pos=(0, 0), text='', indicator_val=False,
            indicator_frame_col=(1, 1, 1, 1), frame_col=(1, 1, 1, 1),
            scale=(1, 1, 1), click_snd=None, over_snd=None,
            text_fg=(1, 1, 1, 1), text_font=None, cmd=None, tra_src=None,
            tra_tra=None):
        self.wdg = DirectCheckButton(
            pos=(pos[0], 1, pos[1]), text=text, indicatorValue=indicator_val,
            indicator_frameColor=indicator_frame_col,
            frameColor=frame_col, scale=scale, clickSound=click_snd,
            rolloverSound=over_snd, text_fg=text_fg, text_font=text_font,
            command=cmd)
        P3dAbs.__init__(self, tra_src, tra_tra)


class P3dOptionMenu(P3dAbs):

    def __init__(
            self, text='', items=[], pos=(0, 0), scale=(1, 1, 1),
            initialitem='', cmd=None, frame_size=(-1, 1, -1, 1),
            click_snd=None, over_snd=None, text_may_change=False,
            text_fg=(1, 1, 1, 1), item_frame_col=(1, 1, 1, 1),
            frame_col=(1, 1, 1, 1), highlight_col=(1, 1, 1, 1),
            text_scale=.05, popup_marker_col=(1, 1, 1, 1),
            item_relief=None, item_text_font=None, text_font=None, tra_src=None,
            tra_tra=None):
        self.wdg = DirectOptionMenu(
            text=text, items=items, pos=(pos[0], 1, pos[1]), scale=scale,
            initialitem=initialitem, command=cmd, frameSize=frame_size,
            clickSound=click_snd, rolloverSound=over_snd,
            textMayChange=text_may_change, text_fg=text_fg,
            item_frameColor=item_frame_col, frameColor=frame_col,
            highlightColor=highlight_col, text_scale=text_scale,
            popupMarker_frameColor=popup_marker_col,
            item_relief=item_relief, item_text_font=item_text_font,
            text_font=text_font)
        P3dAbs.__init__(self, tra_src, tra_tra)
        self._fwd_mth('set', lambda obj: obj.wdg.set)

    @property
    def curr_val(self): return self.wdg.get()

    @property
    def curr_idx(self): return self.wdg.selectedIndex


class P3dEntry(P3dAbs, DirectObject):

    def __init__(
            self, scale=.05, pos=(0, 0), entry_font=None, width=12,
            frame_col=(1, 1, 1, 1), initial_text='', obscured=False,
            cmd=None, focus_in_cmd=None, focus_in_args=[],
            focus_out_cmd=None, focus_out_args=[], parent=None,
            tra_src=None, tra_tra=None, text_fg=(1, 1, 1, 1), on_tab=None,
            on_click=None):
        DirectObject.__init__(self)
        self.wdg = DirectEntry(
            scale=scale, pos=(pos[0], 1, pos[1]), entryFont=entry_font, width=width,
            frameColor=frame_col, initialText=initial_text, obscured=obscured,
            command=cmd, focusInCommand=focus_in_cmd,
            focusInExtraArgs=focus_in_args, focusOutCommand=focus_out_cmd,
            focusOutExtraArgs=focus_out_args, parent=parent,
            text_fg=text_fg)
        P3dAbs.__init__(self, tra_src, tra_tra)
        if on_tab:
            self.on_tab_cb = on_tab
            self.accept('tab-up', self.on_tab)
        if on_click: self.wdg.bind(B1PRESS, on_click)
        self._fwd_mth('set', lambda obj: obj.wdg.set)
        self._fwd_mth('enter_text', lambda obj: obj.wdg.enterText)

    def on_tab(self):
        if self.wdg['focus']: self.on_tab_cb()

    @property
    def text(self): return self.wdg.get()

    def enable(self): self['state'] = NORMAL

    def disable(self): self['state'] = DISABLED

    def destroy(self):
        self.ignore('tab-up')
        self.on_tab_cb = None
        P3dAbs.destroy(self)


class P3dLabel(P3dAbs):

    def __init__(
            self, text='', pos=(0, 0), parent=None, text_wordwrap=10,
            text_align=None, text_fg=(1, 1, 1, 1), text_font=None, scale=.05,
            frame_col=(1, 1, 1, 1), tra_src=None, tra_tra=None, hpr=(0, 0, 0)):
        self.wdg = DirectLabel(
            text=text, pos=(pos[0], 1, pos[1]), parent=parent, text_wordwrap=text_wordwrap,
            text_align=text_align, text_fg=text_fg, text_font=text_font,
            scale=scale, frameColor=frame_col, hpr=hpr)
        P3dAbs.__init__(self, tra_src, tra_tra)
        self._fwd_mth('set_bin', lambda obj: obj.wdg.set_bin)
        self._fwd_mth('set_x', lambda obj: obj.wdg.set_x)
        self._fwd_mth('set_alpha_scale', lambda obj: obj.wdg.set_alpha_scale)


class P3dTxt(P3dBase):

    def __init__(
            self, txt='', pos=(0, 0), scale=.05, wordwrap=12, parent=None,
            fg=(1, 1, 1, 1), font=None, align=None, tra_src=None,
            tra_tra=None):
        str2par = {'bottomleft': base.a2dBottomLeft,
                   'leftcenter': base.a2dLeftCenter}
        str2al = {'left': TextNode.A_left, 'right': TextNode.A_right,
                  'center': TextNode.A_center}
        if parent: parent = str2par[parent]
        if align: align = str2al[align]
        self.wdg = OnscreenText(
            text=txt, pos=pos, scale=scale, wordwrap=wordwrap,
            parent=parent, fg=fg, font=font, align=align)
        P3dBase.__init__(self, tra_src, tra_tra)
        self._fwd_mth('set_r', lambda obj: obj.wdg.set_r)


class P3dFrame(P3dAbs):

    def __init__(self, frame_size=(-1, 1, -1, 1), frame_col=(1, 1, 1, 1),
                 pos=(0, 0), parent=None, texture_coord=False):
        P3dAbs.__init__(self)
        self.wdg = DirectFrame(frameSize=frame_size, frameColor=frame_col,
                               pos=(pos[0], 1, pos[1]), parent=parent)
        if texture_coord: self.wdg['frameTexture'] = Texture()
