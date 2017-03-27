class Singleton(object):

    def __init__(self, klass):
        self.klass, self.instance = klass, None

    def __call__(self, *args, **kwArgs):
        if not self.instance:
            self.instance = self.klass(*args, **kwArgs)
        return self.instance
