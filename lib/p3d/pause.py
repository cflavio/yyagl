from os import pardir  # pardir is .. (parent directory)
from os.path import dirname, abspath, join
from sys import modules
from direct.task import Task
from direct.interval.IntervalGlobal import ivalMgr
from yyagl.gameobject import GameObject


class TaskDec:

    paused_taskchain = 'paused tasks'

    def __init__(self, tsk):
        self.tsk = tsk
        path = dirname(modules[Task.__name__].__file__)
        self.__direct_dir = abspath(join(path, pardir))  # path of direct.*

    def process(self):
        func = self.tsk.get_function()  # ordinary tasks
        mod = func.__module__
        modfile = ''
        if "from '" in str(modules[mod]):
            modfile = str(modules[mod]).split("from '")[1][:-2]
        sys_mod = modfile.find(self.__direct_dir) < 0
        actor_ival = False
        if hasattr(func, 'im_class'):
            actor_ival = func.im_class.__name__ == 'ActorInterval'
        if mod.find('direct.interval') == 0 and not actor_ival:
            self.tsk.interval.pause()  # python-based intervals
            return self.tsk
        if mod not in modules or sys_mod: return self.tsk
        return None

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
        tmp_delay = tsk.remainingTime - d_t
        upon_death = tsk.uponDeath if hasattr(tsk, 'uponDeath') else None
        new_task = taskMgr.doMethodLater(
            tmp_delay, tsk.stored_call, tsk.name, uponDeath=upon_death,
            priority=tsk.stored_priority, extraArgs=tsk.stored_extraArgs)
        if hasattr(tsk, 'remainingTime'): new_task.delayTime = tsk.delayTime

    def resume(self):
        tsk = self.tsk
        if hasattr(tsk, 'interval'):
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
        taskMgr.setupTaskChain(TaskDec.paused_taskchain, frameBudget=0)
        self.__paused_ivals = []
        self.__paused_tasks = []

    @property
    def paused(self):
        tsk = taskMgr.getTasksNamed('__on_frame')[0]
        return tsk.getTaskChain() == TaskDec.paused_taskchain

    def pause_tasks(self):
        is_tsk = lambda tsk: tsk and hasattr(tsk, 'getFunction')
        tasks = [TaskDec(tsk) for tsk in taskMgr.getTasks() if is_tsk(tsk)]
        tasks = [tsk for tsk in tasks
                 if tsk.tsk.get_task_chain() != 'unpausable']
        namefilter = ['igLoop', 'dataLoop', 'ivalLoop', 'collisionLoop',
                      'garbageColletStates', 'audioLoop', 'resetPrevTransform',
                      'eventManager']
        tasks = [tsk for tsk in tasks
                 if tsk.tsk.get_name_prefix() not in namefilter]
        not_none = lambda tsk: tsk is not None
        paused_tasks = list(filter(not_none, [tsk.process() for tsk in tasks]))
        self.__paused_tasks = list(map(TaskDec, paused_tasks))
        for tsk in list(filter(is_tsk, taskMgr.getDoLaters())):
            self.__paused_tasks += [TaskDec(tsk)]
            tsk.remainingTime = tsk.wakeTime - globalClock.get_frame_time()
        list(map(lambda tsk: tsk.pause(), self.__paused_tasks))

    def remove_task(self, tsk):
        list(map(self.__paused_tasks.remove, [ptsk for ptsk in self.__paused_tasks if ptsk.tsk == tsk]))

    def pause(self):
        self.__paused_ivals = ivalMgr.getIntervalsMatching('*')
        self.pause_tasks()
        return self.paused

    def resume(self):
        list(map(lambda ival: ival.resume(), self.__paused_ivals))
        list(map(lambda tsk: tsk.resume(), self.__paused_tasks))
        return self.paused

    def destroy(self): GameObject.destroy(self)
