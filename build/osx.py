from shutil import rmtree, move
from yyagl.build.build import bld_dpath, branch
from yyagl.build.deployng import bld_ng


def bld_osx(target, source, env):  # unused target, source
    bld_ng(env['APPNAME'], osx=True)
    src = '{dst_dir}../dist/{appname}-0.0.0_macosx_10_6_x86_64.tar.xz'
    tgt_file = '{dst_dir}{appname}-{version}-osx.tar.xz'
    src_fmt = src.format(dst_dir=bld_dpath, appname=env['APPNAME'],
                         version=branch)
    tgt_fmt = tgt_file.format(dst_dir=bld_dpath, appname=env['APPNAME'],
                              version=branch)
    move(src_fmt, tgt_fmt)
    rmtree('build')
    rmtree('dist')
