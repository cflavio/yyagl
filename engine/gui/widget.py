class Widget(object):

    def init(self, wdg):
        if hasattr(wdg, 'component') and wdg.hascomponent('text0'):
            self.start_fg = wdg.component('text0').textNode.getTextColor()
        if hasattr(wdg, 'getFrameColor'):
            self.start_frame_col = wdg['frameColor']

    def on_enter(self, pos=None):  # pos is for mouse
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

    def on_exit(self, pos=None):  # pos is for mouse
        if hasattr(self, 'start_fg'):
            self['text_fg'] = self.start_fg
        if hasattr(self, 'start_frame_col'):
            self['frameColor'] = self.start_frame_col
        if hasattr(self, 'getShader') and self.getShader():
            self.setShaderInput('col_offset', 0)
        if hasattr(self, 'setFocus'):
            self['focus'] = 0
            self.setFocus()
