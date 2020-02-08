from os import walk, chdir, getcwd, remove
from os.path import join, getsize, exists, dirname
from subprocess import Popen, PIPE


def exec_cmd(cmd):
    ret = Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True).communicate()
    return ret[0].decode('utf-8').strip()  # '\n'.join(ret)


def _branch():
    return exec_cmd('git symbolic-ref HEAD').split('/')[-1].strip()


def _version():
    pref = ''
    root = dirname(dirname(__file__)) + '/'
    if exists(root + 'assets/version.txt'):
        with open(root + 'assets/version.txt') as fver:
            pref = fver.read().strip() + '-'
    bld_ver = pref + exec_cmd('git rev-parse HEAD')[:7]
    with open(root + 'assets/bld_version.txt', 'w') as fver:
        fver.write(bld_ver)
    return bld_ver


def img_tgt_names(files_):  # list of images' target filenames
    #ext = lambda fname: 'png' if fname.endswith('_png.png') else 'txo'
    return [fname[:fname.rfind('.') + 1] + 'txo' for fname in files_]


def tracks_tgt_fnames():
    ret = []
    tr_root = 'assets/tracks/'
    for droot, dnames, _ in walk(tr_root):
        ret += [tr_root + dname + '/models/track_all.bam' for dname in dnames if droot == tr_root and dname != '__pycache__']
    tr_root = 'assets/cars/'
    for droot, _, filenames in walk(tr_root):
        ret += [droot + '/' + filename.replace('.egg', '.bam') for filename in filenames if filename.endswith('.egg')]
    tr_root = 'assets/models/'
    for droot, _, filename in walk(tr_root):
        ret += [droot + '/' + filename.replace('.egg', '.bam') for filename in filenames if filename.endswith('.egg')]
    return ret
    # return [tr_root + dname + '/track_all.bam'
    #         for _, dnames, _ in walk(tr_root) for dname in dnames]
    # this creates an empty folder assets/models/tracks/tex


def set_path(_bld_path):
    global bld_path
    bld_path = _bld_path + ('/' if not _bld_path.endswith('/') else '')
    return bld_path


def files(_extensions, excl_dirs=[], excl_ends_with=[]):
    return [join(root, fname)
            for root, _, fnames in walk('.')
            for fname in __files_ext(fnames, _extensions)
            if not any(e_d in root.split('/') for e_d in excl_dirs) and
            not any(fname.endswith(e_e) for e_e in excl_ends_with)]


def __files_ext(fnames, _extensions):
    return [fname for fname in fnames
            if any(fname.endswith('.' + ext) for ext in _extensions)]


def size(start_dir='.'):
    sizes = [getsize(join(root, fname))
             for root, _, fnames in walk(start_dir) for fname in fnames]
    return sum(sizes)


class InsideDir(object):

    def __init__(self, dir_):
        self.dir = dir_
        self.old_dir = getcwd()

    def __enter__(self):
        chdir(self.dir)

    def __exit__(self, exc_type, exc_val, exc_tb):
        chdir(self.old_dir)


bld_dpath = 'built/'
branch2ver = {'master': 'dev', 'stable': 'stable'}
branch = branch2ver[_branch()] if _branch() in branch2ver else _branch()
ver = _version()
win_fpath = '{dst_dir}{appname}-%s-windows.exe' % branch
osx_fpath = '{dst_dir}{appname}-%s-osx.zip' % branch
linux_fpath = '{dst_dir}{appname}-%s-linux' % branch
flatpak_fpath = '{dst_dir}{appname}-%s-flatpak' % branch
appimage_fpath = '{dst_dir}{appname}-%s-appimage' % branch
src_fpath = '{dst_dir}{appname}-%s-src.tar.gz' % branch
devinfo_fpath = '{dst_dir}{appname}-%s-devinfo.tar.gz' % branch
test_fpath = '{dst_dir}{appname}-%s-tests.tar.gz' % branch
docs_fpath = '{dst_dir}{appname}-%s-docs.tar.gz' % branch
pdf_fpath = '{dst_dir}{appname}-%s-code.tar.gz' % branch
extensions = ['txt', 'ttf', 'txo', 'egg', 'ogg', 'py', 'lua', 'rst', 'pdef',
              'mo', 'bam']
