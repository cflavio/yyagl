from direct.gui.DirectGuiGlobals import NORMAL, DISABLED


class Widget(object):

    highlight_color_offset = (.3, .3, .3, 0)

    def __init__(self): self.start_txt_color = self.start_frame_color = None

    def get_np(self): return self.img

    def enable(self):
        self['state'] = NORMAL
        self.set_alpha_scale(1)

    def disable(self):
        self['state'] = DISABLED
        self.set_alpha_scale(.25)


class ImgWidget(Widget):

    def init(self, wdg): pass


class FrameWidget(Widget):

    def init(self, wdg):
        self.start_frame_color = wdg.get_np()['frameColor']

    def on_wdg_enter(self, pos=None):  # pos: mouse's position
        np = self.get_np()
        np['frameColor'] = self.start_frame_color + Widget.highlight_color_offset

    def on_wdg_exit(self, pos=None):  # pos: mouse's position
        self.get_np()['frameColor'] = self.start_frame_color


class BtnWidget(FrameWidget):

    def init(self, wdg):
        FrameWidget.init(self, wdg)
        wdg = wdg.get_np()
        self.start_txt_color = wdg.component('text0').textNode.get_text_color()

    def on_arrow(self, direction): pass

    def on_wdg_enter(self, pos=None):  # pos: mouse's position
        FrameWidget.on_wdg_enter(self, pos)
        np = self.get_np()
        np['text_fg'] = self.start_txt_color + Widget.highlight_color_offset
        np.set_shader_input('col_offset', .25)

    def on_wdg_exit(self, pos=None):  # pos: mouse's position
        FrameWidget.on_wdg_exit(self, pos)
        self.get_np()['text_fg'] = self.start_txt_color
        self.get_np()['frameColor'] = self.start_frame_color
        self.get_np().set_shader_input('col_offset', 0)

    def on_enter(self):
        if self['command'] and self['state'] == NORMAL:
            self['command'](*self['extraArgs'])


class EntryWidget(FrameWidget):

    def on_arrow(self, direction): pass

    def on_wdg_enter(self, pos=None):  # pos: mouse's position
        FrameWidget.on_wdg_enter(self, pos)
        self.get_np()['focus'] = 1
        self.get_np().setFocus()

    def on_wdg_exit(self, pos=None):  # pos: mouse's position
        FrameWidget.on_wdg_exit(self, pos)
        self.get_np()['focus'] = 0
        self.get_np().setFocus()


class CheckBtnWidget(BtnWidget):

    def on_enter(self):
        self['indicatorValue'] = not self['indicatorValue']
        BtnWidget.on_enter(self)


class SliderWidget(FrameWidget):

    def on_arrow(self, direction):
        if direction in [(-1, 0, 0), (1, 0, 0)]:
            self.get_np()['value'] += -.1 if direction == (-1, 0, 0) else .1
            return True


class OptionMenuWidget(BtnWidget):

    def on_arrow(self, direction):
        is_hor = direction in [(-1, 0, 0), (1, 0, 0)]
        np = self.get_np()
        if not is_hor and not np.popupMenu.is_hidden():
            old_idx = np.highlightedIndex
            dir2offset = {(0, 0, -1): 1, (0, 0, 1): -1}
            idx = np.highlightedIndex + dir2offset[direction]
            idx = min(len(np['items']) - 1, max(0, idx))
            if old_idx == idx: return True
            fcol = np.component('item%s' % idx)['frameColor']
            old_cmp = np.component('item%s' % old_idx)
            np._unhighlightItem(old_cmp, fcol)
            curr_cmp = np.component('item%s' % idx)
            np._highlightItem(curr_cmp, idx)
            return True

    def on_enter(self):
        np = self.get_np()
        if np.popupMenu.is_hidden():
            np.showPopupMenu()
            np._highlightItem(np.component('item0'), 0)
            return
        else:
            np.selectHighlightedIndex()
            idx = np.selectedIndex
            if np['command']: np['command'](np['items'][idx])
            np.hidePopupMenu()
            idx += -1 if idx else 1
            fcol = np.component('item%s' % idx)['frameColor']
            curr_name = 'item%s' % np.selectedIndex
            np._unhighlightItem(np.component(curr_name), fcol)
            return True
        BtnWidget.on_enter(self)
