from os.path import exists
from os import mkdir
from shutil import move
from yyagl.build.build import bld_dpath, branch


def bld_windows(target, source, env):  # unused target, source
    src = '{dst_dir}../dist/{appname}-{version}_win_amd64.tar.xz'
    tgt_file = '{dst_dir}{appname}-{version}-windows.tar.xz'
    src_fmt = src.format(dst_dir=bld_dpath, appname=env['APPNAME'],
                         version=branch)
    tgt_fmt = tgt_file.format(dst_dir=bld_dpath, appname=env['APPNAME'],
                              version=branch)
    if not exists(bld_dpath): mkdir(bld_dpath)
    if exists(src_fmt): move(src_fmt, tgt_fmt)

    src = '{dst_dir}../build/{appname}-{version}.exe'
    tgt_file = '{dst_dir}{appname}-{version}-windows.exe'
    src_fmt = src.format(dst_dir=bld_dpath, appname=env['APPNAME'],
                         version=branch)
    tgt_fmt = tgt_file.format(dst_dir=bld_dpath, appname=env['APPNAME'],
                              version=branch)
    if exists(src_fmt): move(src_fmt, tgt_fmt)
    # rmtree('build')
    # rmtree('dist')
