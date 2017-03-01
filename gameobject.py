from abc import ABCMeta
from inspect import isclass
from direct.fsm.FSM import FSM
from direct.showbase.DirectObject import DirectObject
from .observer import Subject


class Colleague(Subject):

    def __init__(self, mdt, *args, **kwargs):
        Subject.__init__(self)
        self.mdt = mdt
        self._args = args
        self._kwargs = kwargs
        self.async_build(*args, **kwargs)

    def async_build(self, *args, **kwargs):
        self._end_async()

    def _end_async(self):
        self.sync_build(*self._args, **self._kwargs)
        args = 'on_component_built', self
        taskMgr.doMethodLater(.001, self.mdt.notify, 'wait', args)
        #TODO this is necessary to schedule the next component into the next
        # frame otherwise some dependent components may access a non-existent
        # one. think of something better

    def sync_build(self, *args, **kwargs):
        pass

    def destroy(self):
        self.mdt = None
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

    def __init__(self, obj, init_lst, callback):
        obj.attach(self.on_component_built)
        self.callback = callback
        self.completed = [False for _ in init_lst]
        self.pending = {}
        self.__init_lst = init_lst
        for idx in range(len(init_lst)):
            self.__process_lst(obj, idx)

    def __process_lst(self, obj, idx):
        if not self.__init_lst[idx]:
            self.end_lst(idx)
            return
        comp_info = self.__init_lst[idx].pop(0)
        self.pending[comp_info[1].__name__] = idx
        setattr(obj, comp_info[0], comp_info[1](*comp_info[2]))

    def on_component_built(self, obj):
        self.__process_lst(obj.mdt, self.pending[obj.__class__.__name__])

    def end_lst(self, idx):
        self.completed[idx] = True
        if all(self.completed) and self.callback:
            self.callback()


class GameObjectMdt(Subject):
    __metaclass__ = ABCMeta

    def __init__(self, init_lst=[], callback=None):
        Subject.__init__(self)
        self.comps = self.comp_list(init_lst)
        GODirector(self, init_lst, callback)

    def comp_list(self, init_lst):
        if not init_lst:
            return []
        def process_elm(elm):
            return [elm[0]] if type(elm) == tuple else self.comp_list(elm)
        return process_elm(init_lst[0]) + self.comp_list(init_lst[1:])

    def destroy(self):
        Subject.destroy(self)
        map(lambda comp: getattr(self, comp).destroy(), self.comps)
