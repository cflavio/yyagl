from os import system
from .build import bld_dpath, branch, exec_cmd, test_fpath


def bld_uml(target, source, env):
    system('plantuml yyagl/assets/uml/class_diagram.txt')
