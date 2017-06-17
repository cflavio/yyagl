from direct.gui.DirectGuiGlobals import NORMAL


class Widget(object):

    col_offset = (.3, .3, .3, 0)

    def __init__(self):
        self.start_fg = self.start_frame_col = None

    def init(self, wdg):
        if hasattr(wdg, 'component') and wdg.hascomponent('text0'):
            self.start_fg = wdg.component('text0').textNode.get_text_color()
        if hasattr(wdg, 'getFrameColor'):
            self.start_frame_col = wdg['frameColor']

    def on_wdg_enter(self, pos=None):  # pos is for mouse
        if hasattr(self, 'start_fg'):
            self['text_fg'] = self.start_fg + Widget.col_offset
        if hasattr(self, 'start_frame_col'):
            self['frameColor'] = self.start_frame_col + Widget.col_offset
        if hasattr(self, 'getShader') and self.get_shader():
            self.set_shader_input('col_offset', .25)
        if hasattr(self, 'setFocus'):
            self['focus'] = 1
            self.setFocus()

    def on_wdg_exit(self, pos=None):  # pos is for mouse
        if hasattr(self, 'start_fg'):
            self['text_fg'] = self.start_fg
        if hasattr(self, 'start_frame_col'):
            self['frameColor'] = self.start_frame_col
        if hasattr(self, 'getShader') and self.get_shader():
            self.set_shader_input('col_offset', 0)
        if hasattr(self, 'setFocus'):
            self['focus'] = 0
            self.setFocus()

    def on_arrow(self, direction):
        is_hor = direction in [(-1, 0, 0), (1, 0, 0)]
        is_menu = hasattr(self, 'setItems')
        has_popup_open = is_menu and not self.popupMenu.is_hidden()
        if not is_hor and has_popup_open:
            old_idx = self.highlightedIndex
            dir2offset = {(0, 0, -1): 1, (0, 0, 1): -1}
            idx = self.highlightedIndex + dir2offset[direction]
            idx = min(len(self['items']) - 1, max(0, idx))
            if old_idx != idx:
                fcol = self.component('item%s' % idx)['frameColor']
                old_cmp = self.component('item%s' % old_idx)
                self._unhighlightItem(old_cmp, fcol)
                curr_cmp = self.component('item%s' % idx)
                self._highlightItem(curr_cmp, idx)
            return True
        if is_hor and hasattr(self, 'setValue'):
            self['value'] += -.1 if direction == (-1, 0, 0) else .1
            return True

    def on_enter(self):
        if hasattr(self, 'setIndicatorValue'):
            val = self['indicatorValue']
            self['indicatorValue'] = not val
        if hasattr(self, 'setItems') and self.popupMenu.is_hidden():
            self.showPopupMenu()
            self._highlightItem(self.component('item0'), 0)
            return
        elif hasattr(self, 'setItems') and not self.popupMenu.is_hidden():
            self.selectHighlightedIndex()
            idx = self.selectedIndex
            if self['command']:
                self['command'](self['items'][idx])
            self.hidePopupMenu()
            idx += -1 if idx else 1
            fcol = self.component('item%s' % idx)['frameColor']
            curr_name = 'item%s' % self.selectedIndex
            self._unhighlightItem(self.component(curr_name), fcol)
            return True
        if self['command'] and self['state'] == NORMAL:
            self['command'](*self['extraArgs'])
