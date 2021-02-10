from os import system, makedirs, chdir
from os.path import dirname, realpath, exists, abspath
from shutil import move, rmtree, copytree, copy
from distutils.dir_util import copy_tree
from yyagl.build.build import bld_dpath, branch, InsideDir, size


def bld_linux(target, source, env):  # unused target, source
    ico_fpath = env['ICO_FPATH']
    # chdir('..')  # after the previous command we are in 'dist'
    src = '{dst_dir}../dist/{appname}-{version}_manylinux1_x86_64.tar.xz'
    tgt_file = '{dst_dir}{appname}-{version}-linux_amd64.tar.xz'
    src_fmt = src.format(dst_dir=bld_dpath, appname=env['APPNAME'],
                         version=branch)
    tgt_fmt = tgt_file.format(dst_dir=bld_dpath, appname=env['APPNAME'],
                              version=branch)
    move(src_fmt, tgt_fmt)
    start_dir = abspath('.') + '/'
    if exists(bld_dpath + 'linux'): rmtree(bld_dpath + 'linux')
    makedirs(bld_dpath + 'linux')
    with InsideDir(bld_dpath + 'linux'):
        _do_bld(start_dir, env['APPNAME'], ico_fpath)
    rmtree(bld_dpath + 'linux')


def _do_bld(start_dir, appname, ico_fpath, clean=True):
    _prepare(start_dir)
    _bld(appname, start_dir, ico_fpath)
    _bld_pckgs(appname)
    chdir('../..')
    if not clean: return
    # rmtree('build')
    # rmtree('dist')


def _prepare(start_path):  # unused start_path
    makedirs('img/data')
    curr_path = dirname(realpath(__file__)) + '/'
    copytree(curr_path + 'mojosetup/meta', 'img/meta')
    copytree(curr_path + 'mojosetup/scripts', 'img/scripts')
    copy(curr_path + 'mojosetup/mojosetup_amd64', '.')
    if not exists(curr_path + 'mojosetup/guis'): return
    makedirs('img/guis')
    libfpath = curr_path + 'mojosetup/guis/amd64/libmojosetupgui_gtkplus2.so'
    dst_dpath = 'img/guis/libmojosetupgui_gtkplus2.so'
    copy(libfpath, dst_dpath)


def _bld(appname, start_path, ico_fpath):
    # arch = {'i386': 'i686', 'amd64': 'x86_64'}
    copy(start_path + ico_fpath % '48', 'img/data/icon.png')
    seds = ['version', 'size', 'appname', 'AppName', 'vendorsite']
    sseds = ' '.join(["-e 's/<%s>/{%s}/'" % (sed, sed) for sed in seds])
    tmpl = 'sed -i.bak %s img/scripts/config.lua' % sseds
    cmd = tmpl.format(version=branch, size=size('img'),
                      appname=appname, AppName=appname.capitalize(),
                      vendorsite='ya2.it')
    system(cmd)
    copy_tree('../../build/manylinux1_x86_64', 'img/data')


def _bld_pckgs(appname):
    with InsideDir('img/data'): system('tar -cvf - * | xz > ../pdata.tar.xz')
    system('rm -rf img/data/*')
    move('img/pdata.tar.xz', 'img/data/pdata.tar.xz')
    with InsideDir('img'): system('zip -r ../pdata.zip *')
    system('cat pdata.zip >> ./mojosetup_amd64')
    fdst = '%s-%s-linux_amd64' % (appname, branch)
    move('mojosetup_amd64', fdst)
    system('chmod +x %s-%s-linux_amd64' % (appname, branch))
    fsrc = '%s-%s-linux_amd64' % (appname, branch)
    move(fsrc, '../%s-%s-linux_amd64' % (appname, branch))
