from abc import ABCMeta
from direct.fsm.FSM import FSM
from direct.showbase.DirectObject import DirectObject
from .observer import Subject


class Colleague(Subject):

    def __init__(self, mdt, *args, **kwargs):
        Subject.__init__(self)
        self.notify_tsk = None
        self.mdt = mdt
        self.async_bld(*args, **kwargs)

    def async_bld(self, *args, **kwargs):
        self._end_async(*args, **kwargs)

    def _end_async(self, *args, **kwargs):
        self.sync_bld(*args, **kwargs)
        notify_args = 'on_comp_blt', self
        self.notify_tsk = eng.do_later(.001, self.mdt.notify, notify_args)
        # this is necessary to schedule the next component into the next
        # frame otherwise some dependent components may access a non-existent
        # one. think of something better

    def sync_bld(self, *args, **kwargs):
        pass

    def destroy(self):
        if self.notify_tsk:
            taskMgr.remove(self.notify_tsk)
        self.mdt = self.notify_tsk = None
        Subject.destroy(self)


class Fsm(FSM, Colleague):

    def __init__(self, mdt):
        FSM.__init__(self, self.__class__.__name__)
        Colleague.__init__(self, mdt)

    def destroy(self):
        if self.state:
            self.cleanup()
        Colleague.destroy(self)


class Event(Colleague, DirectObject):

    def destroy(self):
        Colleague.destroy(self)
        self.ignoreAll()


class Audio(Colleague):
    pass


class Ai(Colleague):
    pass


class Gfx(Colleague):
    pass


class Gui(Colleague):
    pass


class Logic(Colleague):
    pass


class Phys(Colleague):
    pass


class GODirector(object):

    def __init__(self, tgt_obj, init_lst, callback):
        self.__obj = tgt_obj
        tgt_obj.attach(self.on_comp_blt)
        self.callback = callback
        self.completed = [False for _ in init_lst]
        self.pending = {}
        self.__init_lst = init_lst
        for idx in range(len(init_lst)):
            self.__process_lst(tgt_obj, idx)

    def __process_lst(self, obj, idx):
        if not self.__init_lst[idx]:
            self.end_lst(idx)
            return
        comp_info = self.__init_lst[idx].pop(0)
        # TODO: define comp_info as a named tuple
        self.pending[comp_info[1].__name__] = idx
        setattr(obj, comp_info[0], comp_info[1](*comp_info[2]))

    def on_comp_blt(self, obj):
        self.__process_lst(obj.mdt, self.pending[obj.__class__.__name__])

    def end_lst(self, idx):
        self.completed[idx] = True
        if all(self.completed):
            if self.callback:
                self.callback()
            self.destroy()

    def destroy(self):
        self.__obj.detach(self.on_comp_blt)
        self.__obj = self.callback = self.__init_lst = None


class GameObject(Subject):
    __metaclass__ = ABCMeta

    def __init__(self, init_lst=None, callback=None):
        Subject.__init__(self)
        self.comp_names = self.__comp_lst(init_lst)
        GODirector(self, init_lst, callback)

    def __comp_lst(self, init_lst):
        if not init_lst:
            return []

        def process_elm(elm):
            return [elm[0]] if isinstance(elm, tuple) else self.__comp_lst(elm)
        return process_elm(init_lst[0]) + self.__comp_lst(init_lst[1:])

    def destroy(self):
        Subject.destroy(self)
        map(lambda cmp: getattr(self, cmp).destroy(), self.comp_names)
