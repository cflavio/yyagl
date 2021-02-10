from direct.fsm.FSM import FSM
from direct.showbase.DirectObject import DirectObject
from yyagl.observer import Subject


class Colleague(Subject):

    eng = None

    def __init__(self, mediator):
        Subject.__init__(self)
        self.mediator = mediator  # refactor: remove it

    def destroy(self):
        self.mediator = None
        Subject.destroy(self)


class FsmColleague(FSM, Colleague):

    def __init__(self, mediator):
        FSM.__init__(self, self.__class__.__name__)
        Colleague.__init__(self, mediator)

    def destroy(self):
        if self.state: self.cleanup()
        Colleague.destroy(self)


class EventColleague(Colleague, DirectObject):

    def destroy(self):
        self.ignoreAll()
        Colleague.destroy(self)


class AudioColleague(Colleague): pass


class AiColleague(Colleague): pass


class GfxColleague(Colleague): pass


class GuiColleague(Colleague): pass


class LogicColleague(Colleague):

    def on_start(self): pass


class PhysColleague(Colleague): pass


class GODirector:

    def __init__(self, tgt_obj, init_lst, end_cb):
        self.__obj = tgt_obj
        tgt_obj.attach(self.on_comp_blt)
        self.end_cb = end_cb
        self.completed = [False for _ in init_lst]
        self.pending = {}
        self.__init_lst = init_lst
        for idx, _ in enumerate(init_lst): self.__process_lst(tgt_obj, idx)

    def __process_lst(self, obj, idx):
        if not self.__init_lst[idx]:
            self.end_lst(idx)
            return
        comp_info = self.__init_lst[idx].pop(0)
        attr_name, cls, arguments = comp_info
        self.pending[cls.__name__] = idx
        setattr(obj, attr_name, cls(*arguments))

    def on_comp_blt(self, obj):
        self.__process_lst(obj.mediator, self.pending[obj.__class__.__name__])

    def end_lst(self, idx):
        self.completed[idx] = True
        if all(self.completed):
            if self.end_cb: self.end_cb()
            self.destroy()

    def destroy(self):
        self.__obj.detach(self.on_comp_blt)
        self.__obj = self.end_cb = self.__init_lst = None


class GameObject(Subject): pass
