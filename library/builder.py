from .panda.panda import LibPanda3D


class LibBuilder(object):

    cls = LibPanda3D

    @staticmethod
    def build(): return LibPanda3D()
