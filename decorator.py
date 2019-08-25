class Decorator:

    def __init__(self, decorated):
        self.__dict__['_decorated'] = decorated

    def __getattr__(self, attr): return getattr(self._decorated, attr)

    def __setattr__(self, attr, value):
        return setattr(self._decorated, attr, value)
