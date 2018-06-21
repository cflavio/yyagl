from .panda.panda import LibraryPanda3D


class LibraryBuilder(object):

    cls = LibraryPanda3D

    @staticmethod
    def build(): return LibraryPanda3D()
