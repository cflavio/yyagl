from os import pardir
from os.path import dirname, abspath, join
from sys import modules
from direct.task import Task
from direct.interval.IntervalGlobal import ivalMgr
from yyagl.library.pause import Pause
from yyagl.library.panda.panda import LibraryPanda3D


class PandaPause(Pause):

    def __init__(self):
        self.__paused_taskchain = 'ya2 paused tasks'
        taskMgr.setupTaskChain(self.__paused_taskchain, frameBudget=0)
        fpath = dirname(modules[Task.__name__].__file__)
        self.direct_dir = abspath(join(fpath, pardir))  # path of direct.*
        self.__paused_ivals = []
        self.__paused_tasks = []

    @property
    def is_paused(self):
        return taskMgr.getTasksNamed('__on_frame')[0].getTaskChain() == self.__paused_taskchain

    def __process_task(self, tsk):
        func = tsk.get_function()  # ordinary tasks
        mod = func.__module__
        # sys_mod = sys.modules[mod].__file__.find(self.direct_dir) < 0
        # runtime: AttributeError: 'module' object has no attribute '__file__'
        modfile = ''
        if "from '" in str(modules[mod]):
            modfile = str(modules[mod]).split("from '")[1][:-2]
        sys_mod = modfile.find(self.direct_dir) < 0
        is_actor_ival = False
        if hasattr(func, 'im_class'):
            is_actor_ival = func.im_class.__name__ == 'ActorInterval'
        if mod.find('direct.interval') == 0 and not is_actor_ival:
            self.__paused_tasks += [tsk]  # python-based intervals
            tsk.interval.pause()
        elif mod not in modules or sys_mod: self.__paused_tasks += [tsk]

    def __pause_tsk(self, tsk):
        has_args = hasattr(tsk, 'getArgs')
        tsk.stored_extraArgs = tsk.get_args() if has_args else None
        if hasattr(tsk, 'getFunction'): tsk.stored_call = tsk.get_function()
        has_p = hasattr(tsk, '_priority')
        tsk.stored_priority = tsk._priority if has_p else tsk.get_sort()
        if hasattr(tsk, 'remainingTime'): tsk.remove()  # do_later tasks
        else:  # ordinary tasks
            tsk.lastactivetime = -tsk.time if hasattr(tsk, 'time') else 0
            tsk.setTaskChain(self.__paused_taskchain)

    def pause_tasks(self):
        self.__paused_tasks = []
        is_tsk = lambda tsk: tsk and hasattr(tsk, 'getFunction')
        tasks = [tsk for tsk in taskMgr.getTasks() if is_tsk(tsk)]
        if LibraryPanda3D.version().startswith('1.10'):
            tasks = [tsk for tsk in tasks if tsk.get_task_chain() != 'unpausable']
        map(self.__process_task, tasks)
        for tsk in [_tsk for _tsk in taskMgr.getDoLaters()if is_tsk(_tsk)]:
            self.__paused_tasks += [tsk]
            tsk.remainingTime = tsk.wakeTime - globalClock.get_frame_time()
        map(self.__pause_tsk, self.__paused_tasks)

    @staticmethod
    def __resume_do_later(tsk):
        d_t = globalClock.get_real_time() - globalClock.get_frame_time()
        temp_delay = tsk.remainingTime - d_t
        upon_death = tsk.uponDeath if hasattr(tsk, 'uponDeath') else None
        # no need to pass appendTask, since if it's already true,
        # the task is already appended to extraArgs
        new_task = taskMgr.doMethodLater(
            temp_delay, tsk.stored_call, tsk.name, uponDeath=upon_death,
            priority=tsk.stored_priority, extraArgs=tsk.stored_extraArgs)
        if hasattr(tsk, 'remainingTime'):  # restore the original delayTime
            new_task.delayTime = tsk.delayTime

    def __resume_tsk(self, tsk):
        if hasattr(tsk, 'interval'):  # it must be python-based intervals
            tsk.interval.resume()
            if hasattr(tsk, 'stored_call'): tsk.set_function(tsk.stored_call)
            return
        if hasattr(tsk, 'remainingTime'):
            self.__resume_do_later(tsk)
            return
        tsk.set_delay(tsk.lastactivetime)  # ordinary tasks
        tsk.set_task_chain('default')
        tsk.clear_delay()  # to avoid assertion error on resume

    def remove_task(self, tsk):
        if tsk in self.__paused_tasks: self.__paused_tasks.remove(tsk)

    def pause(self):
        self.__paused_ivals = ivalMgr.getIntervalsMatching('*')
        self.pause_tasks()
        return self.is_paused

    def resume(self):
        map(lambda ival: ival.resume(), self.__paused_ivals)
        map(self.__resume_tsk, self.__paused_tasks)
        return self.is_paused

    def destroy(self): pass
