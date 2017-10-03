from .panda.panda import LibraryPanda3D
from .panda.vec import Panda3DVec
from .vec import Vec
import sys
import yyagl.engine.vec as _vec


class LibraryBuilder(object):

    @staticmethod
    def build(): return LibraryPanda3D()
