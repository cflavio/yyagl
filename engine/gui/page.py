from direct.gui.DirectButton import DirectButton
from ...gameobject import GameObjectMdt, Gui, Event
from .imgbtn import ImageButton
from direct.interval.LerpInterval import LerpPosInterval
from direct.interval.MetaInterval import Sequence
from direct.interval.FunctionInterval import Wait, Func
from direct.gui.DirectGuiGlobals import ENTER, EXIT, NORMAL, DISABLED
from direct.gui.DirectOptionMenu import DirectOptionMenu
from direct.gui.DirectCheckButton import DirectCheckButton
from direct.gui.DirectSlider import DirectSlider
from panda3d.core import LPoint3f


class PageGui(Gui):

    def __init__(self, mdt, menu):
        Gui.__init__(self, mdt)
        self.menu = menu
        self.widgets = []
        self.build_page()
        self.update_texts()
        self.curr_wdg = None
        self.curr_wdg = self.get_next_widget((-.1, 0, -1), (-3.6, 1, 1))
        (self._on_enter_img_btn if self.curr_wdg.__class__ == ImageButton else self._on_enter)(self.curr_wdg)

    def build_page(self):
        self.__build_back_btn()
        self._set_buttons()
        self.transition_enter()

    def on_arrow(self, direction):
        if direction in [(-1, 0, 0), (1, 0, 0)] and self.curr_wdg.__class__ == DirectSlider:
            dval = -.1 if direction == (-1, 0, 0) else .1
            self.curr_wdg['value'] += dval
            return
        next_wdg = self.get_next_widget(direction)
        if not next_wdg: return
        if self.curr_wdg.__class__ == DirectSlider:
            self._on_exit_slider(self.curr_wdg)
        elif self.curr_wdg.__class__ == ImageButton:
            self._on_exit_img_btn(self.curr_wdg)
        else:
            self._on_exit(self.curr_wdg)
        self.curr_wdg = next_wdg
        if self.curr_wdg.__class__ == DirectSlider:
            self._on_enter_slider(self.curr_wdg)
        elif self.curr_wdg.__class__ == ImageButton:
            self._on_enter_img_btn(self.curr_wdg)
        else:
            self._on_enter(self.curr_wdg)

    def on_enter(self):
        if self.curr_wdg.__class__ == DirectCheckButton:
            self.curr_wdg['indicatorValue'] = not self.curr_wdg['indicatorValue']
        if self.curr_wdg.__class__ == DirectOptionMenu:
            self.curr_wdg.showPopupMenu()
            self.curr_wdg._highlightItem(self.curr_wdg.component('item0'), 0)
            self.mdt.event.ignoreAll()
            self.mdt.event.accept('arrow_up-up', self.on_arrow_opt, [-1])
            self.mdt.event.accept('arrow_down-up', self.on_arrow_opt, [1])
            self.mdt.event.accept('enter-up', self.on_enter_opt)
            return
        if self.curr_wdg and self.curr_wdg['command'] and self.curr_wdg['state'] == NORMAL:
            self.curr_wdg['command'](*self.curr_wdg['extraArgs'])

    def on_arrow_opt(self, d):
        old_idx = self.curr_wdg.highlightedIndex
        idx = self.curr_wdg.highlightedIndex + d
        idx = min(len(self.curr_wdg['items']) - 1, max(0, idx))
        if old_idx != idx:
            fc = self.curr_wdg.component('item%s' % idx)['frameColor']
            self.curr_wdg._unhighlightItem(self.curr_wdg.component('item%s' % old_idx), fc)
            self.curr_wdg._highlightItem(self.curr_wdg.component('item%s' % idx), idx)

    def on_enter_opt(self):
        self.curr_wdg.selectHighlightedIndex()
        if self.curr_wdg['command']: self.curr_wdg['command'](self.curr_wdg['items'][self.curr_wdg.selectedIndex])
        self.curr_wdg.hidePopupMenu()
        self.mdt.event.ignoreAll()
        idx = (self.curr_wdg.selectedIndex - 1) if self.curr_wdg.selectedIndex else (self.curr_wdg.selectedIndex + 1)
        fc = self.curr_wdg.component('item%s' % idx)['frameColor']
        self.curr_wdg._unhighlightItem(self.curr_wdg.component('item%s' % self.curr_wdg.selectedIndex), fc)
        self.enable()

    def __get_dot(self, wdg, direction, start=None):
        start_pos = start if start else self.curr_wdg.get_pos(aspect2d)
        vec = wdg.get_pos(aspect2d) - start_pos
        vec.normalize()
        return vec.dot(direction)

    def __next_factor(self, wdg, direction, start=None):
        start_pos = start if start else self.curr_wdg.get_pos(aspect2d)
        dot = self.__get_dot(wdg, direction, start)
        wdg_pos = wdg.get_pos(aspect2d)
        if wdg.__class__ == DirectSlider:
            wdg_pos = LPoint3f(wdg_pos[0], 1, wdg_pos[2])
        dist = (wdg_pos - start_pos).length()
        if direction in [(-1, 0, 0), (1, 0, 0)]:
            proj_dist = abs(wdg_pos[0] - start_pos[0])
        else:
            proj_dist = abs(wdg_pos[2] - start_pos[2])
        if direction in [(-1, 0, 0), (1, 0, 0)]:
            weights = [.5, .5]
        else:
            weights = [.1, .9]
        return weights[0] * (dot * dot) + weights[1] * (1 - proj_dist)# + .6 * (1 - dist / 4.0)

    def get_next_widget(self, direction, start=None):
        wdgs = [wdg for wdg in self.widgets if wdg.__class__ in [DirectButton, DirectCheckButton, DirectSlider, DirectOptionMenu, ImageButton]]
        wdgs = filter(lambda wdg: wdg['state'] != DISABLED, wdgs)
        if self.curr_wdg: wdgs.remove(self.curr_wdg)
        wdgs = filter(lambda wdg: self.__get_dot(wdg, direction, start) > .1, wdgs)
        if not wdgs: return
        return max(wdgs, key=lambda wdg: self.__next_factor(wdg, direction, start))

    def _set_buttons(self):
        for wdg in self.widgets:
            if wdg.__class__ in [ImageButton]:
                wdg.bind(ENTER, self._on_enter_img_btn, [wdg])
                wdg.bind(EXIT, self._on_exit_img_btn, [wdg])
            elif wdg.__class__ in [DirectButton, DirectOptionMenu, DirectCheckButton]:
                wdg.start_fg = wdg.component('text0').textNode.getTextColor()
                wdg.start_frame_col = wdg['frameColor']
                wdg.bind(ENTER, self._on_enter, [wdg])
                wdg.bind(EXIT, self._on_exit, [wdg])
            elif wdg.__class__ in [DirectSlider]:
                wdg.start_frame_col = wdg['frameColor']
                wdg.bind(ENTER, self._on_enter_slider, [wdg])
                wdg.bind(EXIT, self._on_exit_slider, [wdg])

    def _on_enter(self, wdg, pos=None):
        _fg = wdg.start_fg
        _fc = wdg.start_frame_col
        wdg['text_fg'] = (_fg[0] + .3, _fg[1] + .3, _fg[2] + .3, _fg[3])
        wdg['frameColor'] = (_fc[0] + .3, _fc[1] + .3, _fc[2] + .3, _fc[3])

    def _on_exit(self, wdg, pos=None):
        wdg['text_fg'] = wdg.start_fg
        wdg['frameColor'] = wdg.start_frame_col

    def _on_enter_slider(self, wdg, pos=None):
        _fc = wdg.start_frame_col
        wdg['frameColor'] = (_fc[0] + .3, _fc[1] + .3, _fc[2] + .3, _fc[3])

    def _on_exit_slider(self, wdg, pos=None):
        wdg['frameColor'] = wdg.start_frame_col

    def _on_enter_img_btn(self, wdg, pos=None):
        wdg.setShaderInput('col_scale', .25)

    def _on_exit_img_btn(self, wdg, pos=None):
        wdg.setShaderInput('col_scale', 0)

    def transition_enter(self):
        self.update_texts()
        for wdg in self.widgets:
            pos = wdg.get_pos()
            start_pos = (pos[0] - 3.6, pos[1], pos[2])
            wdg.set_pos(start_pos)
            Sequence(
                Wait(abs(pos[2] - 1) / 4),
                LerpPosInterval(wdg, .5, pos, blendType='easeInOut')
            ).start()
        self.enable()

    def enable(self):
        self.mdt.event.accept('arrow_left-up', self.on_arrow, [(-1, 0, 0)])
        self.mdt.event.accept('arrow_right-up', self.on_arrow, [(1, 0, 0)])
        self.mdt.event.accept('arrow_up-up', self.on_arrow, [(0, 0, 1)])
        self.mdt.event.accept('arrow_down-up', self.on_arrow, [(0, 0, -1)])
        self.mdt.event.accept('enter-up', self.on_enter)

    def transition_exit(self, destroy=True):
        for wdg in self.widgets:
            pos = wdg.get_pos()
            end_pos = (pos[0] + 3.6, pos[1], pos[2])
            seq = Sequence(
                Wait(abs(pos[2] - 1) / 4),
                LerpPosInterval(wdg, .5, end_pos, blendType='easeInOut'),
                Func(wdg.destroy if destroy else wdg.hide))
            if not destroy:
                seq.append(Func(wdg.set_pos, pos))
            seq.start()

    @staticmethod
    def transl_text(obj, text_src, text_transl):
        obj.__text_src = text_src
        obj.__class__.transl_text = property(lambda self: _(self.__text_src))

    def update_texts(self):
        tr_wdg = [wdg for wdg in self.widgets if hasattr(wdg, 'transl_text')]
        for wdg in tr_wdg:
            wdg['text'] = wdg.transl_text

    def __build_back_btn(self):
        self.widgets += [DirectButton(
            text='', pos=(0, 1, -.8), command=self.__on_back,
            **self.menu.gui.btn_args)]
        PageGui.transl_text(self.widgets[-1], 'Back', _('Back'))
        self.widgets[-1]['text'] = self.widgets[-1].transl_text

    def __on_back(self):
        self.mdt.event.on_back()
        self.notify('on_back')

    def show(self):
        map(lambda wdg: wdg.show(), self.widgets)
        self.transition_enter()

    def hide(self):
        #map(lambda wdg: wdg.hide(), self.widgets)
        self.transition_exit(False)
        self.mdt.event.ignoreAll()

    def destroy(self):
        self.menu = None
        self.transition_exit()


class PageEvent(Event):

    def on_back(self):
        pass


class Page(GameObjectMdt):
    gui_cls = PageGui
    event_cls = PageEvent

    def __init__(self, menu):
        self.menu = menu
        GameObjectMdt.__init__(self, self.init_lst)

    @property
    def init_lst(self):
        return [
            [('fsm', self.fsm_cls, [self])],
            [('gfx', self.gfx_cls, [self])],
            [('phys', self.phys_cls, [self])],
            [('event', self.event_cls, [self])],
            [('gui', self.gui_cls, [self, self.menu])],
            [('logic', self.logic_cls, [self])],
            [('audio', self.audio_cls, [self])],
            [('ai', self.ai_cls, [self])]]
