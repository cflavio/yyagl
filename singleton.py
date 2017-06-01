class Singleton(object):

    def __init__(self, cls):
        self.cls, self.inst = cls, None

    def __call__(self, *args, **kw_args):
        if not self.inst:
            self.inst = self.cls(*args, **kw_args)
        return self.inst
