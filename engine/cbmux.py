from threading import Lock


class CallbackMux():
    # this is a sort of "multiplexer" i.e. it manages callbacks from threads
    # and redirect them to the main thread (this prevents deadlocks)

    def __init__(self):
        self.lock = Lock()
        self.callbacks = []
        taskMgr.add(self.process_callbacks, 'processing callbacks')

    def add_cb(self, func, args):
        with self.lock: self.callbacks += [(func, args)]

    def process_callbacks(self, task):
        with self.lock:
            callbacks = self.callbacks[:]
            self.callbacks = []
        for func, args in callbacks: func(*args)
        return task.cont
