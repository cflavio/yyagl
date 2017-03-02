from direct.gui.DirectGuiGlobals import NORMAL


class Widget(object):

    def init(self, wdg):
        if hasattr(wdg, 'component') and wdg.hascomponent('text0'):
            self.start_fg = wdg.component('text0').textNode.getTextColor()
        if hasattr(wdg, 'getFrameColor'):
            self.start_frame_col = wdg['frameColor']

    def on_wdg_enter(self, pos=None):  # pos is for mouse
        if hasattr(self, 'start_fg'):
            _fg = self.start_fg
            self['text_fg'] = (_fg[0] + .3, _fg[1] + .3, _fg[2] + .3, _fg[3])
        if hasattr(self, 'start_frame_col'):
            _fc = self.start_frame_col
            self['frameColor'] = (_fc[0] + .3, _fc[1] + .3, _fc[2] + .3,
                                  _fc[3])
        if hasattr(self, 'getShader') and self.getShader():
            self.setShaderInput('col_offset', .25)
        if hasattr(self, 'setFocus'):
            self['focus'] = 1
            self.setFocus()

    def on_wdg_exit(self, pos=None):  # pos is for mouse
        if hasattr(self, 'start_fg'):
            self['text_fg'] = self.start_fg
        if hasattr(self, 'start_frame_col'):
            self['frameColor'] = self.start_frame_col
        if hasattr(self, 'getShader') and self.getShader():
            self.setShaderInput('col_offset', 0)
        if hasattr(self, 'setFocus'):
            self['focus'] = 0
            self.setFocus()

    def on_arrow(self, direction):
        is_hor = direction in [(-1, 0, 0), (1, 0, 0)]
        if not is_hor and hasattr(self, 'setItems') and not self.popupMenu.isHidden():
            old_idx = self.highlightedIndex
            idx = self.highlightedIndex + {(0, 0, -1): 1, (0, 0, 1): -1}[direction]
            idx = min(len(self['items']) - 1, max(0, idx))
            if old_idx != idx:
                fc = self.component('item%s' % idx)['frameColor']
                old_cmp = self.component('item%s' % old_idx)
                self._unhighlightItem(old_cmp, fc)
                curr_cmp = self.component('item%s' % idx)
                self._highlightItem(curr_cmp, idx)
            return True
        if is_hor and hasattr(self, 'setValue'):
            dval = -.1 if direction == (-1, 0, 0) else .1
            self['value'] += dval
            return True

    def on_enter(self):
        if hasattr(self, 'setIndicatorValue'):
            val = self['indicatorValue']
            self['indicatorValue'] = not val
        if hasattr(self, 'setItems') and self.popupMenu.isHidden():
            self.showPopupMenu()
            self._highlightItem(self.component('item0'), 0)
            return
        elif hasattr(self, 'setItems') and not self.popupMenu.isHidden():
            self.selectHighlightedIndex()
            idx = self.selectedIndex
            if self['command']:
                self['command'](self['items'][idx])
            self.hidePopupMenu()
            idx = (idx - 1) if idx else (idx + 1)
            fc = self.component('item%s' % idx)['frameColor']
            curr_name = 'item%s' % self.selectedIndex
            self._unhighlightItem(self.component(curr_name), fc)
            return True
        if self['command'] and self['state'] == NORMAL:
            self['command'](*self['extraArgs'])
