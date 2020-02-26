from distutils.cmd import Command
from distutils.log import INFO
from setuptools import setup
from build.src import bld_src


class SourcePkgCommand(Command):

    user_options = []

    def initialize_options(self): pass

    def finalize_options(self): pass

    def run(self):
        self.announce(
            'Building source package',
            level=INFO)
        bld_src(None, None, {'APPNAME': 'yyagl'})


if __name__ == '__main__':
    setup(
        cmdclass={
            'source_pkg': SourcePkgCommand,
        },
        name='Yyagl',
        version=0.12
    )
