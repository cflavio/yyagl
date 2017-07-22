from inspect import getmro
from panda3d.core import LPoint3f
from direct.gui.DirectButton import DirectButton
from direct.interval.LerpInterval import LerpPosInterval
from direct.interval.MetaInterval import Sequence
from direct.interval.FunctionInterval import Wait, Func
from direct.gui.DirectGuiGlobals import ENTER, EXIT, DISABLED
from direct.gui.DirectOptionMenu import DirectOptionMenu
from direct.gui.DirectCheckButton import DirectCheckButton
from direct.gui.DirectSlider import DirectSlider
from direct.gui.DirectEntry import DirectEntry
from ...gameobject import GameObject, Gui, Event
from ...facade import Facade
from .imgbtn import ImgBtn
from .widget import Widget


class PageGui(Gui):

    def __init__(self, mdt, menu_args):
        Gui.__init__(self, mdt)
        self.menu_args = menu_args
        self.widgets = []
        self.bld_page()
        self.update_texts()
        self.curr_wdg = self.__next_wdg((-.1, 0, -1), (-3.6, 1, 1))
        if self.curr_wdg:
            self.curr_wdg.on_wdg_enter()

    def bld_page(self, back_btn=True):
        if back_btn:
            self.__bld_back_btn()
        self._set_buttons()
        self.transition_enter()
        eng.cursor_top()

    def add_widget(self, wdg):
        self.widgets += [wdg]

    def on_arrow(self, direction):
        if not self.curr_wdg:
            return
        if not self.curr_wdg.on_arrow(direction):
            next_wdg = self.__next_wdg(direction)
            if next_wdg:
                self.curr_wdg.on_wdg_exit()
                self.curr_wdg = next_wdg
                self.curr_wdg.on_wdg_enter()

    def on_enter(self):
        if not self.curr_wdg:
            return
        if self.curr_wdg.on_enter():
            self.enable()

    def __dot(self, wdg, direction, start=None):
        start_pos = start if start else self.curr_wdg.get_pos(aspect2d)
        vec = wdg.get_pos(aspect2d) - start_pos
        vec.normalize()
        return vec.dot(direction)

    def __next_factor(self, wdg, direction, start=None):
        start_pos = start if start else self.curr_wdg.get_pos(aspect2d)
        dot = self.__dot(wdg, direction, start)
        wdg_pos = wdg.get_pos(aspect2d)
        if wdg.__class__ == DirectSlider:
            wdg_pos = LPoint3f(wdg_pos[0], 1, wdg_pos[2])
        if direction in [(-1, 0, 0), (1, 0, 0)]:
            proj_dist = abs(wdg_pos[0] - start_pos[0])
        else:
            proj_dist = abs(wdg_pos[2] - start_pos[2])
        if direction in [(-1, 0, 0), (1, 0, 0)]:
            weights = [.5, .5]
        else:
            weights = [.1, .9]
        return weights[0] * (dot * dot) + weights[1] * (1 - proj_dist)

    def __next_wdg(self, direction, start=None):
        iclss = [DirectButton, DirectCheckButton, DirectSlider,
                 DirectOptionMenu, ImgBtn, DirectEntry]  # interactive classes
        inter = lambda wdg: any(pcl in iclss for pcl in getmro(wdg.__class__))
        wdgs = [wdg for wdg in self.widgets if inter(wdg)]
        wdgs = filter(lambda wdg: wdg['state'] != DISABLED, wdgs)
        if hasattr(self, 'curr_wdg') and self.curr_wdg:
            wdgs.remove(self.curr_wdg)
        pos_dot = lambda wdg: self.__dot(wdg, direction, start) > .1
        wdgs = filter(pos_dot, wdgs)
        if not wdgs:
            return
        nextfact = lambda wdg: self.__next_factor(wdg, direction, start)
        return max(wdgs, key=nextfact)

    def _set_buttons(self):
        for wdg in self.widgets:
            clsname = wdg.__class__.__name__ + 'Widget'
            wdg.__class__ = type(clsname, (wdg.__class__, Widget), {})
            wdg.init(wdg)
            if hasattr(wdg, 'bind'):
                wdg.bind(ENTER, wdg.on_wdg_enter)
                wdg.bind(EXIT, wdg.on_wdg_exit)

    def transition_enter(self):
        self.update_texts()
        for wdg in self.widgets:
            pos = wdg.get_pos()
            wdg.set_pos((pos[0] - 3.6, pos[1], pos[2]))
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
        # text_transl is not used: why are we passing it?
        obj.__text_src = text_src
        obj.__class__.transl_text = property(lambda self: _(self.__text_src))

    def update_texts(self):
        tr_wdg = [wdg for wdg in self.widgets if hasattr(wdg, 'transl_text')]
        for wdg in tr_wdg:
            wdg['text'] = wdg.transl_text

    def __bld_back_btn(self):
        self.widgets += [DirectButton(
            text='', pos=(0, 1, -.8), command=self.__on_back,
            **self.menu_args.btn_args)]
        PageGui.transl_text(self.widgets[-1], 'Back', _('Back'))
        self.widgets[-1]['text'] = self.widgets[-1].transl_text

    def __on_back(self):
        self.mdt.event.on_back()
        self.notify('on_back')

    def show(self):
        map(lambda wdg: wdg.show(), self.widgets)
        self.transition_enter()

    def hide(self):
        self.transition_exit(False)
        self.mdt.event.ignoreAll()

    def destroy(self):
        self.menu_args = None
        self.transition_exit()


class PageEvent(Event):

    def on_back(self):
        pass


class PageFacade(Facade):

    def __init__(self):
        self._fwd_mth_lazy('show', lambda: self.gui.show)
        self._fwd_mth_lazy('hide', lambda: self.gui.hide)
        self._fwd_mth_lazy('attach_obs', lambda: self.gui.attach)
        self._fwd_mth_lazy('detach_obs', lambda: self.gui.detach)


class Page(GameObject, PageFacade):
    gui_cls = PageGui
    event_cls = PageEvent

    def __init__(self, menu_args, menu):
        # we should not pass the menu to the page. now we do this since menu's
        # clients attach to the menu for observing its events, but them are
        # fired by pages. maybe the menu should attach clients' methods to the
        # pages when they are pushed.
        PageFacade.__init__(self)
        self.menu_args = menu_args
        self.menu = menu
        GameObject.__init__(self, self.init_lst)

    @property
    def init_lst(self):
        return [
            [('event', self.event_cls, [self])],
            [('gui', self.gui_cls, [self, self.menu_args])]]
