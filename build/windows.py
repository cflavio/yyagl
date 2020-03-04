from os import system, remove, rename, walk
from os.path import exists
from shutil import move, rmtree, copytree, copy
from distutils.dir_util import copy_tree
from yyagl.build.build import ver, bld_dpath, branch, InsideDir
from yyagl.build.deployng import bld_ng


def bld_windows(target, source, env):
    src = '{dst_dir}../dist/{appname}-{version}_win_amd64.tar.xz'
    tgt_file = '{dst_dir}{appname}-{version}-windows.tar.xz'
    src_fmt = src.format(dst_dir=bld_dpath, appname=env['APPNAME'],
                         version=branch)
    tgt_fmt = tgt_file.format(dst_dir=bld_dpath, appname=env['APPNAME'],
                              version=branch)
    if exists(src_fmt): move(src_fmt, tgt_fmt)

    src = '{dst_dir}../build/{appname}-{version}.exe'
    tgt_file = '{dst_dir}{appname}-{version}-windows.exe'
    src_fmt = src.format(dst_dir=bld_dpath, appname=env['APPNAME'],
                         version=branch)
    tgt_fmt = tgt_file.format(dst_dir=bld_dpath, appname=env['APPNAME'],
                              version=branch)
    if exists(src_fmt): move(src_fmt, tgt_fmt)
    #rmtree('build')
    #rmtree('dist')
