from inspect import getmro
from panda3d.core import LVecBase2f
from direct.gui.DirectGuiGlobals import ENTER, EXIT
from yyagl.library.gui import Btn, Slider, CheckBtn, OptionMenu, Entry, \
    Label, Img, Frame, Text
from yyagl.library.ivals import Seq, Wait, PosIval, Func
from yyagl.engine.vec import Vec2
from ...gameobject import GameObject, GuiColleague, EventColleague
from ...facade import Facade
from .imgbtn import ImgBtn
from .widget import FrameWidget, ImgWidget, BtnWidget, EntryWidget, \
    CheckBtnWidget, SliderWidget, OptionMenuWidget


class PageGui(GuiColleague):

    def __init__(self, mediator, menu_args, players=[0]):
        GuiColleague.__init__(self, mediator)
        self.enable_tsk = None
        self.menu_args = menu_args
        self.players = players
        self.widgets = []
        self.build()
        self.translate()
        self.curr_wdgs = []
        for player in players:
            self.curr_wdgs += [self.__next_wdg((-.1, 0, -1), player, (-3.6, 1, 1))]
            if self.curr_wdgs[-1]: self.curr_wdgs[-1].on_wdg_enter(None, player)

    def build(self, back_btn=True, exit_behav=False):
        if back_btn: self.__build_back_btn(exit_behav)
        self._set_widgets()
        self.transition_enter()
        self.eng.cursor_top()

    def add_widgets(self, widgets): self.widgets += widgets

    def on_arrow(self, direction, player):
        if not self.curr_wdgs[player]: return
        catch_cmd = self.curr_wdgs[player].on_arrow(direction)
        # e.g. up/down in a combobox or left/right in a slider
        if catch_cmd: return
        next_wdg = self.__next_wdg(direction, player)
        if not next_wdg: return
        self.curr_wdgs[player].on_wdg_exit(None, player)
        self.curr_wdgs[player] = next_wdg
        self.curr_wdgs[player].on_wdg_enter(None, player)

    def on_enter(self, player):
        if not self.curr_wdgs[player]: return
        arg = player if len(self.players) > 1 else None
        if self.curr_wdgs[player].on_enter(arg): self.enable([player])

    @property
    def buttons(self):
        is_btn = lambda wdg: Btn in getmro(wdg.__class__)
        return [wdg for wdg in self.widgets if is_btn(wdg)]

    def __currwdg2wdg_dot_direction(self, wdg, direction, player, start=None):
        start_pos = start if start else self.curr_wdgs[player].get_pos(aspect2d)
        vec = wdg.get_pos(aspect2d) - start_pos
        vec = Vec2(vec.x, vec.z).normalize()
        return vec.dot(Vec2(direction[0], direction[2]))

    def __next_weight(self, wdg, direction, player, start=None):
        start_pos = start if start else self.curr_wdgs[player].get_pos(aspect2d)
        dot = self.__currwdg2wdg_dot_direction(wdg, direction, player, start)
        wdg_pos = wdg.get_pos(aspect2d)
        # if 'Slider' in wdg.__class__ .__name__:
        #     wdg_pos = LPoint3f(wdg_pos[0], 1, wdg_pos[2])
        axis = 0 if direction in [(-1, 0, 0), (1, 0, 0)] else 2
        proj_dist = abs(wdg_pos[axis] - start_pos[axis])
        weights = [.5, .5] if not axis else [.1, .9]
        return weights[0] * (dot * dot) + weights[1] * (1 - proj_dist)

    def __next_wdg(self, direction, player, start=None):
        # interactive classes
        iclss = [Btn, CheckBtn, Slider, OptionMenu, ImgBtn, Entry]
        inter = lambda wdg: any(pcl in iclss for pcl in getmro(wdg.__class__))
        wdgs = [wdg for wdg in self.widgets if inter(wdg)]
        wdgs = filter(lambda wdg: wdg.is_enabled, wdgs)
        if hasattr(self, 'curr_wdgs') and player < len(self.curr_wdgs) and self.curr_wdgs[player] \
                and self.curr_wdgs[player] in wdgs:
                # the last check for this case: multiple players appear on the
                # same button, one player clicks it, another moves from it
            wdgs.remove(self.curr_wdgs[player])
        mth = self.__currwdg2wdg_dot_direction
        in_direction = lambda wdg: mth(wdg, direction, player, start) > .1
        wdgs = filter(in_direction, wdgs)
        if not wdgs: return
        nextweight = lambda wdg: self.__next_weight(wdg, direction, player, start)
        return max(wdgs, key=nextweight)

    def _set_widgets(self):
        map(self.__set_widget, self.widgets)

    @staticmethod
    def __set_widget(wdg):
        libwdg2wdg = {
            FrameWidget: [Frame],
            SliderWidget: [Slider],
            BtnWidget: [Btn, Label],
            OptionMenuWidget: [OptionMenu],
            CheckBtnWidget: [CheckBtn],
            EntryWidget: [Entry],
            ImgWidget: [Img, Text]}
        for libwdg, wdgcls in libwdg2wdg.items():
            if any(cls in getmro(wdg.__class__) for cls in wdgcls):
                par_cls = libwdg
        clsname = wdg.__class__.__name__ + 'Widget'
        wdg.__class__ = type(clsname, (wdg.__class__, par_cls), {})
        wdg.init(wdg)
        if hasattr(wdg, 'bind'):
            wdg.bind(ENTER, wdg.on_wdg_enter)
            wdg.bind(EXIT, wdg.on_wdg_exit)

    def transition_enter(self):
        self.translate()
        map(self.__set_enter_transition, self.widgets)
        self.enable(self.players)

    @staticmethod
    def __set_enter_transition(wdg):
        pos = wdg.get_pos()
        wdg.set_pos(pos - (3.6, 0, 0))
        Seq(
            Wait(abs(pos[2] - 1) / 4),
            PosIval(wdg.get_np(), .5, pos)
        ).start()

    def enable_navigation(self, players):
        if self.enable_tsk:
            self.eng.rm_do_later(self.enable_tsk)
            self.enable_tsk = None
        self.enable_tsk = self.eng.do_later(.01, self.enable_navigation_aux, [players])

    def enable_navigation_aux(self, players):
        for player in players:
            nav = self.menu_args.nav.navinfo_lst[player]
            evts = [
                (nav.left, self.on_arrow, [(-1, 0, 0), player]),
                (nav.right, self.on_arrow, [(1, 0, 0), player]),
                (nav.up, self.on_arrow, [(0, 0, 1), player]),
                (nav.down, self.on_arrow, [(0, 0, -1), player]),
                (nav.fire, self.on_enter, [player])]
            map(lambda args: self.mediator.event.accept(*args), evts)

    def disable_navigation(self, players):
        if self.enable_tsk:
            self.eng.rm_do_later(self.enable_tsk)
            self.enable_tsk = None
        for player in players:
            nav = self.menu_args.nav.navinfo_lst[player]
            evts = [nav.left, nav.right, nav.up, nav.down, nav.fire]
            map(self.mediator.event.ignore, evts)

    def enable(self, players):
        self.enable_navigation(players)
        map(lambda wdg: wdg.enable(), self.widgets)

    def disable(self, players):
        if self.enable_tsk:
            self.eng.rm_do_later(self.enable_tsk)
            self.enable_tsk = None
        self.disable_navigation(players)
        map(lambda wdg: wdg.disable(), self.widgets)

    def transition_exit(self, destroy=True):
        map(lambda wdg: self.__set_exit_transition(wdg, destroy), self.widgets)
        self.disable(self.players)

    @staticmethod
    def __set_exit_transition(wdg, destroy):
        pos = wdg.get_pos()
        end_pos = (pos[0] + 3.6, pos[1], pos[2])
        seq = Seq(
            Wait(abs(pos[2] - 1) / 4),
            PosIval(wdg.get_np(), .5, end_pos),
            Func(wdg.destroy if destroy else wdg.hide))
        if not destroy: seq.append(Func(wdg.set_pos, pos))
        seq.start()

    def translate(self):
        tr_wdg = [wdg for wdg in self.widgets if hasattr(wdg, 'bind_transl')]
        for wdg in tr_wdg: wdg.wdg['text'] = wdg.bind_transl

    def __build_back_btn(self, exit_behav):
        tra_src = 'Quit' if exit_behav else 'Back'
        tra_tra = _('Quit') if exit_behav else _('Back')
        callback = self._on_quit if exit_behav else self._on_back
        self.widgets += [Btn(
            text='', pos=(-.2, 1, -.92), command=callback,
            tra_src=tra_src, tra_tra=tra_tra, **self.menu_args.btn_args)]

    def _on_back(self): self.notify('on_back', self.__class__.__name__)

    def _on_quit(self): self.notify('on_quit', self.__class__.__name__)

    def show(self):
        visible_widgets = [wdg for wdg in self.widgets if wdg.was_visible]
        map(lambda wdg: wdg.show(), visible_widgets)
        self.transition_enter()

    def hide(self):
        for wdg in self.widgets: wdg.was_visible = not wdg.is_hidden()
        self.transition_exit(False)
        self.notify('on_hide')

    def destroy(self):
        self.transition_exit()
        self.menu_args = None


class PageEvent(EventColleague):

    def on_back(self): pass

    def on_quit(self): pass


class PageFacade(Facade):

    def __init__(self):
        fwds = [
            ('show', lambda obj: obj.gui.show),
            ('hide', lambda obj: obj.gui.hide),
            ('enable', lambda obj: obj.gui.enable),
            ('disable', lambda obj: obj.gui.disable),
            ('enable_navigation', lambda obj: obj.gui.enable_navigation),
            ('disable_navigation', lambda obj: obj.gui.disable_navigation),
            ('attach_obs', lambda obj: obj.gui.attach),
            ('detach_obs', lambda obj: obj.gui.detach)]
        map(lambda args: self._fwd_mth(*args), fwds)


class Page(GameObject, PageFacade):

    gui_cls = PageGui
    event_cls = PageEvent

    def __init__(self, menu_args, players=[0]):
        # refactor: pages e.g. yyagl/engine/gui/mainpage.py don't call this
        PageFacade.__init__(self)
        self.menu_args = menu_args
        self.players = players
        GameObject.__init__(self, self.init_lst)
        self.gui.attach(self.on_hide)
        self.gui.attach(self.on_back)
        self.gui.attach(self.on_quit)

    @property
    def init_lst(self):
        return [
            [('event', self.event_cls, [self])],
            [('gui', self.gui_cls, [self, self.menu_args, self.players])]]

    def on_hide(self): self.event.ignoreAll()

    def on_back(self, cls_name): self.event.on_back()  # unused arg

    def on_quit(self, cls_name): self.event.on_quit()  # unused arg

    def destroy(self):
        GameObject.destroy(self)
        PageFacade.destroy(self)
