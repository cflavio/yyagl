from os import system
from .build import bld_dpath, branch, exec_cmd, test_fpath


def bld_uml(target, source, env):
    system('plantuml yyagl/assets/uml/class_diagram.txt')
    system('plantuml yyagl/assets/uml/sequence_diagrams.txt')
    system('convert yyagl/assets/uml/sequence_diagrams*.png yyagl/assets/uml/sequence_diagrams.pdf')
    system('rm yyagl/assets/uml/sequence_diagrams*.png')
    system('pdfnup --nup 3x2 -o yyagl/assets/uml/sequence_diagrams.pdf yyagl/assets/uml/sequence_diagrams.pdf')
