from direct.gui.DirectButton import DirectButton
from ...gameobject import GameObjectMdt, Gui, Event
from direct.interval.LerpInterval import LerpPosInterval
from direct.interval.MetaInterval import Sequence
from direct.interval.FunctionInterval import Wait, Func
from direct.gui.DirectGuiGlobals import ENTER, EXIT
from direct.gui.DirectOptionMenu import DirectOptionMenu
from direct.gui.DirectCheckButton import DirectCheckButton
from direct.gui.DirectSlider import DirectSlider


class PageGui(Gui):

    def __init__(self, mdt, menu):
        Gui.__init__(self, mdt)
        self.menu = menu
        self.widgets = []
        self.build_page()
        self.update_texts()

    def build_page(self):
        self.__build_back_btn()
        self._set_buttons()
        self.transition_enter()

    def _set_buttons(self):
        for wdg in self.widgets:
            if wdg.__class__ in [DirectButton, DirectOptionMenu, DirectCheckButton]:
                wdg.start_fg = wdg.component('text0').textNode.getTextColor()
                wdg.start_frame_col = wdg['frameColor']
                wdg.bind(ENTER, self._on_enter, [wdg])
                wdg.bind(EXIT, self._on_exit, [wdg])
            if wdg.__class__ in [DirectSlider]:
                wdg.start_frame_col = wdg['frameColor']
                wdg.bind(ENTER, self._on_enter_slider, [wdg])
                wdg.bind(EXIT, self._on_exit_slider, [wdg])

    def _on_enter(self, wdg, pos):
        _fg = wdg.start_fg
        _fc = wdg.start_frame_col
        wdg['text_fg'] = (_fg[0] + .2, _fg[1] + .2, _fg[2] + .2, _fg[3])
        wdg['frameColor'] = (_fc[0] + .2, _fc[1] + .2, _fc[2] + .2, _fc[3])

    def _on_exit(self, wdg, pos):
        wdg['text_fg'] = wdg.start_fg
        wdg['frameColor'] = wdg.start_frame_col

    def _on_enter_slider(self, wdg, pos):
        _fc = wdg.start_frame_col
        wdg['frameColor'] = (_fc[0] + .2, _fc[1] + .2, _fc[2] + .2, _fc[3])

    def _on_exit_slider(self, wdg, pos):
        wdg['frameColor'] = wdg.start_frame_col

    def transition_enter(self):
        for wdg in self.widgets:
            pos = wdg.get_pos()
            start_pos = (pos[0] - 3.6, pos[1], pos[2])
            wdg.set_pos(start_pos)
            Sequence(
                Wait(abs(pos[2] - 1) / 4),
                LerpPosInterval(wdg, .5, pos, blendType='easeInOut')
            ).start()

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
    def transl_text(obj, text_src):
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
        PageGui.transl_text(self.widgets[-1], 'Back')
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
