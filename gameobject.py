from abc import ABCMeta
from direct.fsm.FSM import FSM
from direct.showbase.DirectObject import DirectObject
from .observer import Subject


class Colleague(Subject):

    eng = None

    def __init__(self, mediator, *args, **kwargs):
        Subject.__init__(self)
        self.notify_tsk = None
        self.mediator = mediator  # refactor: remove it
        self.async_bld(*args, **kwargs)

    def async_bld(self, *args, **kwargs):
        self._end_async(*args, **kwargs)

    def _end_async(self, *args, **kwargs):
        self.sync_bld(*args, **kwargs)
        args = 'on_comp_blt', self
        self.notify_tsk = self.eng.do_later(.001, self.mediator.notify, args)
        # since on_comp_blt is fired from __init__, when it's catched by
        # GODirector's on_comp_blt, it triggers __process_lst, but since
        # __init__ it's not finished, __process_lst's setattrs is not
        # concluded, so the following components don't see the previous one.
        # maybe it's better to remove this kind of creation process, and use
        # a more standard one

    def sync_bld(self, *args, **kwargs):
        pass

    def destroy(self):
        if self.notify_tsk:
            taskMgr.remove(self.notify_tsk)
        self.mediator = self.notify_tsk = None
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


class LogicColleague(Colleague): pass


class PhysColleague(Colleague): pass


class GODirector(object):

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


class GameObject(Subject):
    __metaclass__ = ABCMeta

    def __init__(self, init_lst=[], end_cb=None):
        Subject.__init__(self)
        self.comp_names = self.__comp_lst(init_lst)
        GODirector(self, init_lst, end_cb)
        # in Panda 1.10 change the approach: use async/await in place
        # of this

    def __comp_lst(self, init_lst):
        if not init_lst: return []
        return self.__process_elm(init_lst[0]) + self.__comp_lst(init_lst[1:])

    def __process_elm(self, elm):
        return [elm[0]] if isinstance(elm, tuple) else self.__comp_lst(elm)

    def destroy(self):
        list(map(lambda cmp: getattr(self, cmp).destroy(), self.comp_names))
        Subject.destroy(self)
