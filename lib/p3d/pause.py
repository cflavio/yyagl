from os import pardir
from os.path import dirname, abspath, join
from sys import modules
from direct.task import Task
from direct.interval.IntervalGlobal import ivalMgr
from yyagl.gameobject import GameObject


class TaskDec(object):

    paused_taskchain = None

    def __init__(self, tsk):
        self.tsk = tsk
        path = dirname(modules[Task.__name__].__file__)
        self.__direct_dir = abspath(join(path, pardir))  # path of direct.*

    def process(self):
        func = self.tsk.get_function()  # ordinary tasks
        mod = func.__module__
        # sys_mod = sys.modules[mod].__file__.find(self.__direct_dir) < 0
        # runtime: AttributeError: 'module' object has no attribute '__file__'
        modfile = ''
        if "from '" in str(modules[mod]):
            modfile = str(modules[mod]).split("from '")[1][:-2]
        sys_mod = modfile.find(self.__direct_dir) < 0
        is_actor_ival = False
        if hasattr(func, 'im_class'):
            is_actor_ival = func.im_class.__name__ == 'ActorInterval'
        if mod.find('direct.interval') == 0 and not is_actor_ival:
            self.tsk.interval.pause()  # python-based intervals
            return self.tsk
        elif mod not in modules or sys_mod: return self.tsk

    def pause(self):
        tsk = self.tsk
        has_args = hasattr(tsk, 'getArgs')
        tsk.stored_extraArgs = tsk.get_args() if has_args else None
        if hasattr(tsk, 'getFunction'): tsk.stored_call = tsk.get_function()
        has_p = hasattr(tsk, '_priority')
        tsk.stored_priority = tsk._priority if has_p else tsk.get_sort()
        if hasattr(tsk, 'remainingTime'): tsk.remove()  # do_later tasks
        else:  # ordinary tasks
            tsk.lastactivetime = -tsk.time if hasattr(tsk, 'time') else 0
            tsk.setTaskChain(TaskDec.paused_taskchain)

    def __resume_do_later(self):
        tsk = self.tsk
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

    def resume(self):
        tsk = self.tsk
        if hasattr(tsk, 'interval'):  # it must be python-based intervals
            tsk.interval.resume()
            if hasattr(tsk, 'stored_call'): tsk.set_function(tsk.stored_call)
            return
        if hasattr(tsk, 'remainingTime'):
            self.__resume_do_later()
            return
        tsk.set_delay(tsk.lastactivetime)  # ordinary tasks
        tsk.set_task_chain('default')
        tsk.clear_delay()  # to avoid assertion error on resume


class P3dPause(GameObject):

    def __init__(self):
        GameObject.__init__(self)
        TaskDec.paused_taskchain = 'yyagl paused tasks'
        taskMgr.setupTaskChain(TaskDec.paused_taskchain, frameBudget=0)
        self.__paused_ivals = []
        self.__paused_tasks = []

    @property
    def paused(self):
        tsk = taskMgr.getTasksNamed('__on_frame')[0]
        return tsk.getTaskChain() == TaskDec.paused_taskchain

    def pause_tasks(self):
        self.__paused_tasks = []
        is_tsk = lambda tsk: tsk and hasattr(tsk, 'getFunction')
        tasks = [TaskDec(tsk) for tsk in taskMgr.getTasks() if is_tsk(tsk)]
        if self.eng.lib.version.startswith('1.10'):
            tasks = [tsk for tsk in tasks
                     if tsk.tsk.get_task_chain() != 'unpausable']
        paused_tasks = map(lambda tsk: tsk.process(), tasks)
        self.__paused_tasks += [tsk for tsk in paused_tasks if tsk]
        for tsk in [_tsk for _tsk in taskMgr.getDoLaters()if is_tsk(_tsk)]:
            self.__paused_tasks += [tsk]
            tsk.remainingTime = tsk.wakeTime - globalClock.get_frame_time()
        map(lambda tsk: TaskDec(tsk).pause(), self.__paused_tasks)

    def remove_task(self, tsk):
        if tsk in self.__paused_tasks: self.__paused_tasks.remove(tsk)

    def pause(self):
        self.__paused_ivals = ivalMgr.getIntervalsMatching('*')
        self.pause_tasks()
        return self.paused

    def resume(self):
        map(lambda ival: ival.resume(), self.__paused_ivals)
        map(lambda tsk: TaskDec(tsk).resume(), self.__paused_tasks)
        return self.paused

    def destroy(self): GameObject.destroy(self)
