class Clock:

    def __init__(self, pause):
        self.__paused_time = 0
        self.__curr_stopped_time = 0
        pause.logic.attach(self.on_pause)
        pause.logic.attach(self.on_resume)

    @property
    def time(self): return globalClock.get_frame_time() - self.__paused_time

    def on_pause(self): self.__curr_stopped_time = globalClock.get_frame_time()

    def on_resume(self):
        self.__paused_time += globalClock.get_frame_time() - self.__curr_stopped_time
