class Singleton(type):

    _insts = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._insts:
            cls._insts[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._insts[cls]
