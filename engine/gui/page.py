from inspect import getmro
from panda3d.core import LVecBase2f
from direct.gui.DirectGuiGlobals import ENTER, EXIT
from yyagl.lib.gui import Btn, Slider, CheckBtn, OptionMenu, Entry, \
    Label, Img, Frame, Text
from yyagl.lib.ivals import Seq, Wait, PosIval, Func
from yyagl.engine.vec import Vec2
from yyagl.engine.gui.gui import left, right, up, down
from yyagl.gameobject import GameObject, GuiColleague, EventColleague
from yyagl.facade import Facade
from yyagl.engine.gui.imgbtn import ImgBtn
from yyagl.lib.p3d.widget import FrameMixin, ImgMixin, BtnMixin, EntryMixin, \
    CheckBtnMixin, SliderMixin, OptionMenuMixin


class PageGui(GuiColleague):

    def __init__(self, mediator, menu_props, players=[0]):
        GuiColleague.__init__(self, mediator)
        self.enable_tsk = None
        self.menu_props = menu_props
        self.players = players
        self.widgets = []
        self.build()
        self.translate()
        self.curr_wdgs = []
        for player in players:
            self.curr_wdgs += [self.__next_wdg((-.1, -1), player, Vec2(-3.6, 1))]
            if self.curr_wdgs[-1]: self.curr_wdgs[-1].on_wdg_enter(None, player)

    def build(self, back_btn=True, exit_behav=False):
        if back_btn: self.__build_back_btn(exit_behav)
        self._set_widgets()
        self.transition_enter()
        self.eng.cursor_top()

    def add_widgets(self, widgets): self.widgets += widgets

    def on_arrow(self, direction, player):
        if not self.curr_wdgs[player]: return
        processed_cmd = self.curr_wdgs[player].on_arrow(direction)
        # e.g. up/down in a combobox or left/right in a slider
        if processed_cmd: return
        next_wdg = self.__next_wdg(direction, player)
        if not next_wdg: return
        self.curr_wdgs[player].on_wdg_exit(None, player)
        self.curr_wdgs[player] = next_wdg
        self.curr_wdgs[player].on_wdg_enter(None, player)

    def on_enter(self, player):
        if not self.curr_wdgs[player]: return
        arg = player if len(self.players) > 1 else None
        if self.curr_wdgs[player].on_enter(arg): self.enable([player])
        # wdg.on_enter returns True when it is an option widget

    @property
    def buttons(self):
        is_btn = lambda wdg: Btn in getmro(wdg.__class__)
        return [wdg for wdg in self.widgets if is_btn(wdg)]

    def __direction_dot_dwg(self, wdg, direction, player, start=None):
        if start: start_pos = start
        else: start_pos = self.curr_wdgs[player].pos
        return (wdg.pos - start_pos).norm.dot(direction)

    def __next_weight(self, wdg, direction, player, start=None):
        if start: start_pos = start
        else: start_pos = self.curr_wdgs[player].pos
        dot = self.__direction_dot_dwg(wdg, direction, player, start)
        if direction in [(-1, 0), (1, 0)]:
            proj_dist = abs(wdg.pos.x - start_pos.x)
        else: proj_dist = abs(wdg.pos.y - start_pos.y)
        weights = [.5, .5] if direction in [left, right] else [.1, .9]
        return weights[0] * (dot * dot) + weights[1] * (1 - proj_dist)

    def __next_wdg(self, direction, player, start=None):
        # interactive classes
        iclss = [Btn, CheckBtn, Slider, OptionMenu, ImgBtn, Entry]
        inter = lambda wdg: any(pcl in iclss for pcl in getmro(wdg.__class__))
        allwdgs = [wdg for wdg in self.widgets if inter(wdg)]
        wdgs = filter(lambda wdg: wdg.is_enabled, allwdgs)
        if player < len(self.curr_wdgs) and self.curr_wdgs[player] \
                and self.curr_wdgs[player] in wdgs:
                # the last check for this case: multiple players appear on the
                # same button, one player clicks it, another moves from it
            wdgs.remove(self.curr_wdgs[player])
        mth = self.__direction_dot_dwg
        in_direction = lambda wdg: mth(wdg, direction, player, start) > .1
        dirwdgs = filter(in_direction, wdgs)
        if not dirwdgs: return
        nextweight = lambda wdg: self.__next_weight(wdg, direction, player, start)
        return max(dirwdgs, key=nextweight)

    def _set_widgets(self): map(lambda wdg: wdg.set_widget(), self.widgets)

    def transition_enter(self):
        self.translate()
        map(lambda wdg: wdg.set_enter_transition(), self.widgets)
        self.enable(self.players)

    def translate(self): map(lambda wdg: wdg.translate(), self.widgets)

    def enable_navigation(self, players):
        if self.enable_tsk: self.eng.rm_do_later(self.enable_tsk)
        self.enable_tsk = self.eng.do_later(.01, self.enable_navigation_aux, [players])

    def enable_navigation_aux(self, players):
        for player in players:
            nav = self.menu_props.nav.navinfo_lst[player]
            evts = [
                (nav.left, self.on_arrow, [left, player]),
                (nav.right, self.on_arrow, [right, player]),
                (nav.up, self.on_arrow, [up, player]),
                (nav.down, self.on_arrow, [down, player]),
                (nav.fire, self.on_enter, [player])]
            map(lambda args: self.mediator.event.accept(*args), evts)

    def disable_navigation(self, players):
        if self.enable_tsk:
            self.enable_tsk = self.eng.rm_do_later(self.enable_tsk)
        for player in players:
            nav = self.menu_props.nav.navinfo_lst[player]
            evts = [nav.left, nav.right, nav.up, nav.down, nav.fire]
            map(self.mediator.event.ignore, evts)

    def enable(self, players):
        self.enable_navigation(players)
        map(lambda wdg: wdg.enable(), self.widgets)

    def disable(self, players):
        if self.enable_tsk:
            self.enable_tsk = self.eng.rm_do_later(self.enable_tsk)
        self.disable_navigation(players)
        map(lambda wdg: wdg.disable(), self.widgets)

    def transition_exit(self, destroy=True):
        map(lambda wdg: wdg.set_exit_transition(destroy), self.widgets)
        self.disable(self.players)

    def __build_back_btn(self, exit_behav):
        tra_src = 'Quit' if exit_behav else 'Back'
        tra_tra = _('Quit') if exit_behav else _('Back')
        callback = self._on_quit if exit_behav else self._on_back
        btn = Btn(text='', pos=(-.2, -.92), cmd=callback,
                  tra_src=tra_src, tra_tra=tra_tra, **self.menu_props.btn_args)
        self.widgets += [btn]

    def _on_back(self): self.notify('on_back', self.__class__.__name__)
    # refactor: notify should pass the sender, so these arguments would be
    # useless

    def _on_quit(self): self.notify('on_quit', self.__class__.__name__)

    def show(self):
        visible_widgets = [wdg for wdg in self.widgets if wdg.was_visible]
        map(lambda wdg: wdg.show(), visible_widgets)
        self.transition_enter()

    def hide(self):
        for wdg in self.widgets: wdg.was_visible = not wdg.hidden
        self.transition_exit(False)
        self.notify('on_hide')

    def destroy(self):
        self.transition_exit()
        self.menu_props = None


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

    def __init__(self, menu_props, players=[0]):
        # refactor: pages e.g. yyagl/engine/gui/mainpage.py don't call this
        PageFacade.__init__(self)
        self.menu_props = menu_props
        self.players = players
        GameObject.__init__(self, self.init_lst)
        map(self.gui.attach, [self.on_hide, self.on_back, self.on_quit])

    @property
    def init_lst(self):
        return [
            [('event', self.event_cls, [self])],
            [('gui', self.gui_cls, [self, self.menu_props, self.players])]]

    def on_hide(self): self.event.ignoreAll()

    def on_back(self, cls_name): self.event.on_back()  # unused arg

    def on_quit(self, cls_name): self.event.on_quit()  # unused arg

    def destroy(self):
        for cls in Page.__bases__: cls.destroy(self)
