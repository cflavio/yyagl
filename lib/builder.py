from yyagl.lib.p3d.p3d import LibP3d


class LibBuilder:
    '''This classe builds the implementation of the library abstraction  (for
    the Dependency Inversion Principle).'''

    @staticmethod
    def build():
        '''This method actually builds the library implementation.
        Now it builds Panda3D's implementation layer, but it may be used as a
        dispatcher (e.g. for new Panda3D versions).'''
        return LibP3d()
