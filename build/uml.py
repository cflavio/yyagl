from os import system, walk, remove, makedirs
from os.path import exists
from shutil import move, rmtree
from .build import bld_dpath, branch, exec_cmd, test_fpath


def bld_uml(target, source, env):
    system('plantuml yyagl/assets/uml/class_diagram.txt')
    system('plantuml yyagl/assets/uml/sequence_diagrams.txt')
    system('convert yyagl/assets/uml/sequence_diagrams*.png yyagl/assets/uml/sequence_diagrams.pdf')
    system('rm yyagl/assets/uml/sequence_diagrams*.png')
    system('pdfnup --nup 3x2 -o yyagl/assets/uml/sequence_diagrams.pdf yyagl/assets/uml/sequence_diagrams.pdf')
    auto_classes()

def auto_classes():
    if not exists('built/tmp_uml'): makedirs('built/tmp_uml')
    for root, _, filenames in walk('.'):
        for filename in filenames:
            if not root.startswith('./wvenv/') and \
                    not root.startswith('./venv/')and \
                    not root.startswith('./yyagl/thirdparty/') and \
                    filename.endswith('.py') and \
                    not filename.endswith('__init__.py'):
                _root = root[2:]
                path = _root + ('/' if _root else '') + filename
                name = path[:-3].replace('/', '_')
                system('pyreverse -o png -p %s %s' % (name, path))
                fname = 'classes_' + name + '.png'
                if exists(fname): move(fname, 'built/tmp_uml/' + fname)
    system('convert -page a5 -rotate 90 -background white built/tmp_uml/classes_*.png built/tmp_uml/uml_classes.pdf')
    system('pdfnup --nup 3x2 -o built/uml_classes.pdf built/tmp_uml/uml_classes.pdf')
    rmtree('built/tmp_uml')
