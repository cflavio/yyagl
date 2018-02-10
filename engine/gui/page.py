from inspect import getmro
from panda3d.core import LPoint3f
from yyagl.library.gui import Btn
from direct.interval.LerpInterval import LerpPosInterval
from direct.interval.MetaInterval import Sequence
from direct.interval.FunctionInterval import Wait, Func
from direct.gui.DirectGuiGlobals import ENTER, EXIT, DISABLED
from direct.gui.DirectOptionMenu import DirectOptionMenu
from direct.gui.DirectCheckButton import DirectCheckButton
from direct.gui.DirectSlider import DirectSlider
from direct.gui.DirectEntry import DirectEntry
from ...gameobject import GameObject, GuiColleague, EventColleague
from ...facade import Facade
from .imgbtn import ImgBtn
from .widget import Widget


class PageGui(GuiColleague):

    def __init__(self, mediator, menu_args):
        GuiColleague.__init__(self, mediator)
        self.menu_args = menu_args
        self.widgets = []
        self.build()
        self.translate()
        self.curr_wdg = self.__next_wdg((-.1, 0, -1), (-3.6, 1, 1))
        if self.curr_wdg: self.curr_wdg.on_wdg_enter()

    def build(self, back_btn=True):
        if back_btn: self.__build_back_btn()
        self._set_buttons()
        self.transition_enter()
        self.eng.cursor_top()

    def add_widgets(self, widgets): self.widgets += widgets

    def on_arrow(self, direction):
        if not self.curr_wdg: return
        catch_cmd = self.curr_wdg.on_arrow(direction)
        # e.g. up/down in a combobox or left/right in a slider
        if catch_cmd: return
        next_wdg = self.__next_wdg(direction)
        if not next_wdg: return
        self.curr_wdg.on_wdg_exit()
        self.curr_wdg = next_wdg
        self.curr_wdg.on_wdg_enter()

    def on_enter(self):
        if not self.curr_wdg: return
        if self.curr_wdg.on_enter(): self.enable()

    @property
    def buttons(self):
        is_btn = lambda wdg: Btn in getmro(wdg.__class__)
        return [wdg for wdg in self.widgets if is_btn(wdg)]

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
        iclss = [Btn, DirectCheckButton, DirectSlider,
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
        self.translate()
        for wdg in self.widgets:
            pos = wdg.get_pos()
            wdg.set_pos((pos[0] - 3.6, pos[1], pos[2]))
            Sequence(
                Wait(abs(pos[2] - 1) / 4),
                LerpPosInterval(wdg.get_np(), .5, pos, blendType='easeInOut')
            ).start()
        self.enable()

    def enable(self):
        evts=[
            ('arrow_left-up', self.on_arrow, [(-1, 0, 0)]),
            ('arrow_right-up', self.on_arrow, [(1, 0, 0)]),
            ('arrow_up-up', self.on_arrow, [(0, 0, 1)]),
            ('arrow_down-up', self.on_arrow, [(0, 0, -1)]),
            ('enter', self.on_enter)]
        map(lambda args: self.mediator.event.accept(*args), evts)

    def disable(self):
        evts=['arrow_left-up', 'arrow_right-up', 'arrow_up-up',
              'arrow_down-up', 'enter']
        map(self.mediator.event.ignore, evts)

    def transition_exit(self, destroy=True):
        for wdg in self.widgets:
            pos = wdg.get_pos()
            end_pos = (pos[0] + 3.6, pos[1], pos[2])
            seq = Sequence(
                Wait(abs(pos[2] - 1) / 4),
                LerpPosInterval(wdg.get_np(), .5, end_pos, blendType='easeInOut'),
                Func(wdg.destroy if destroy else wdg.hide))
            if not destroy:
                seq.append(Func(wdg.set_pos, pos))
            seq.start()

    @staticmethod
    def bind_transl(obj, text_src, text_transl):
        # text_transl is not used, anyway we need it since we have this kind of
        # use: wdg.bind_transl('example str', _('example str'))
        # this allows to change translations on the fly keeping the source
        # text for remapping it later
        obj.text_src_tra = text_src
        obj.__class__.bind_transl = property(lambda self: _(self.text_src_tra))

    def translate(self):
        tr_wdg = [wdg for wdg in self.widgets if hasattr(wdg, 'bind_transl')]
        for wdg in tr_wdg: wdg['text'] = wdg.bind_transl

    def __build_back_btn(self):
        self.widgets += [Btn(
            text='', pos=(-.2, 1, -.8), command=self._on_back,
            **self.menu_args.btn_args)]
        PageGui.bind_transl(self.widgets[-1], 'Back', _('Back'))
        self.widgets[-1]['text'] = self.widgets[-1].bind_transl

    def _on_back(self):
        self.mediator.event.on_back()
        self.notify('on_back', self.__class__.__name__)

    def show(self):
        map(lambda wdg: wdg.show(), self.widgets)
        self.transition_enter()

    def hide(self):
        self.transition_exit(False)
        self.mediator.event.ignoreAll()

    def destroy(self):
        self.menu_args = None
        self.transition_exit()


class PageEvent(EventColleague):

    def on_back(self): pass


class PageFacade(Facade):

    def __init__(self):
        fwds =[
            ('show', lambda obj: obj.gui.show),
            ('hide', lambda obj: obj.gui.hide),
            ('enable', lambda obj: obj.gui.enable),
            ('disable', lambda obj: obj.gui.disable),
            ('attach_obs', lambda obj: obj.gui.attach),
            ('detach_obs', lambda obj: obj.gui.detach)]
        map(lambda args: self._fwd_mth(*args), fwds)


class Page(GameObject, PageFacade):

    gui_cls = PageGui
    event_cls = PageEvent

    def __init__(self, menu_args):
        PageFacade.__init__(self)
        self.menu_args = menu_args
        GameObject.__init__(self, self.init_lst)

    @property
    def init_lst(self):
        return [
            [('event', self.event_cls, [self])],
            [('gui', self.gui_cls, [self, self.menu_args])]]

    def destroy(self):
        GameObject.destroy(self)
        PageFacade.destroy(self)
