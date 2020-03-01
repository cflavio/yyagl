from os import getcwd
from collections import namedtuple
from distutils.cmd import Command
from setuptools import setup
from build.build import files
from build.src import bld_src
from build.devinfo import bld_devinfo
from build.docs import bld_docs
from build.pdf import bld_pdfs
from build.uml import bld_uml
from build.unittests import bld_ut
from build.imgs import bld_images


class AbsCmd(Command):

    env = {'APPNAME': 'yyagl'}
    user_options = [('cores', None, '#cores')]

    def initialize_options(self): self.cores = 0

    def finalize_options(self): AbsCmd.env['CORES'] = self.cores


class SourcePkgCmd(AbsCmd):

    def run(self): bld_src(None, None, AbsCmd.env)


class DevInfoCmd(AbsCmd):

    def run(self):
        def cond_yyagl(src):
            thirdparty = str(src).startswith('yyagl/thirdparty/')
            venv = str(src).startswith('venv/')
            racing = str(src).startswith('yyagl/racing/')
            return thirdparty or venv or racing or \
                str(src).startswith('yyagl/tests')
        dev_conf = {'devinfo_yyagl': cond_yyagl}
        AbsCmd.env['DEV_CONF'] = dev_conf
        bld_devinfo(None, files(['py']), AbsCmd.env)


class DocsCmd(AbsCmd):

    def run(self):
        AbsCmd.env['DOCS_PATH'] = getcwd() + '/..'
        bld_docs(None, None, AbsCmd.env)


class PDFCmd(AbsCmd):

    def run(self):
        PDFInfo = namedtuple('PDFInfo', 'lng root fil excl')
        yyagl_fil = ['./build/*', './engine/*', './lib/*',
                     './tests/*']
        yyagl_lst = [
            PDFInfo('python', '.', '*.py', yyagl_fil),
            PDFInfo('c', '.', '*.vert *.frag', yyagl_fil)]
        binfo_lst = [
            ('python', '*.py *.pdef'), ('lua', 'config.lua'),
            ('', '*.rst *.css_t *.conf'), ('html', '*.html'), ('javascript', '*.js')]
        build_lst = [PDFInfo(binfo[0], 'build', binfo[1], [])
                     for binfo in binfo_lst]
        pdf_conf = {
            'yyagl': yyagl_lst,
            'lib': [PDFInfo('python', './lib', '*.py', [])],
            'build': build_lst,
            'engine': [PDFInfo('python', './engine', '*.py',
                       ['./engine/gui/*', './engine/network/*'])],
            'engine_gui': [PDFInfo('python', './engine/gui', '*.py', [])],
            'engine_network': [PDFInfo('python', './engine/network', '*.py', [])],
            'tests': [PDFInfo('python', './tests', '*.py', [])]}
        AbsCmd.env['PDF_CONF'] = pdf_conf
        bld_pdfs(None, None, AbsCmd.env)


class UMLCmd(AbsCmd):

    def run(self):
        AbsCmd.env['UML_FILTER'] = []
        bld_uml(None, None, AbsCmd.env)


class TestsCmd(AbsCmd):

    def run(self): bld_ut(None, None, AbsCmd.env)


class ImagesCmd(AbsCmd):

    def run(self):
        bld_images(
            None, files(['jpg', 'png'], ['models'], ['_png.png']), AbsCmd.env)


if __name__ == '__main__':
    setup(
        cmdclass={
            'source_pkg': SourcePkgCmd,
            'devinfo': DevInfoCmd,
            'docs': DocsCmd,
            'pdf': PDFCmd,
            'uml': UMLCmd,
            'tests': TestsCmd,
            'images': ImagesCmd},
        name='Yyagl',
        version=0.12)
