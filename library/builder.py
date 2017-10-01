from .panda3d.panda3d import LibraryPanda3D


class LibraryBuilder(object):

    @staticmethod
    def build(): return LibraryPanda3D()
