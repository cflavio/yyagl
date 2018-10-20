from .p3d.p3d import LibP3d


class LibBuilder(object):

    cls = LibP3d

    @staticmethod
    def build(): return LibP3d()
