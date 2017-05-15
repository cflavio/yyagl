from os import walk, chdir, getcwd
from os.path import join, getsize
from subprocess import Popen, PIPE


bld_cmd = (
    'pdeploy -o  {path} {nointernet} -n {name} -N {Name} ' +
    '-v {version} -a ya2.it -A "Ya2" -l "GPLv3" -L license.txt ' +
    "-e flavio@ya2.it -t width=800 -t height=600 -P {platform} " +
    "-i '%s16_png.png' -i '%s32_png.png' -i '%s48_png.png' " +
    "-i '%s128_png.png' -i '%s256_png.png' {p3d_path} installer") % (
    ('assets/images/icon/icon',) * 5)


def exec_cmd(cmd):
    ret = Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True).communicate()
    return '\n'.join(ret)


def __get_branch():
    return exec_cmd('git symbolic-ref HEAD').split('/')[-1].strip()


def __get_version():
    with open('assets/version.txt') as fver:
        return fver.read().strip() + '-' + exec_cmd('git rev-parse HEAD')[:7]


def image_extensions(files):
    ext = lambda fname: 'png' if fname.endswith('_png.psd') else 'dds'
    return [fname[:fname.rfind('.') + 1] + ext(fname) for fname in files]


def track_files():
    tr_root = 'assets/models/tracks/'
    for _, dirnames, _ in walk(tr_root):
        return [tr_root + dname + '/track_all.bam' for dname in dirnames]


def set_path(_path):
    global path
    path = _path + ('/' if not _path.endswith('/') else '')
    return path


def get_files(_extensions, excl_dirs=[]):
    def files_ext(fnames):
        return [
            fname for fname in fnames
            if any(fname.endswith('.' + ext) for ext in _extensions)]
    return [join(root, fname)
            for root, _, fnames in walk('.')
            for fname in files_ext(fnames)
            if not excl_dirs or not
            any(e_d in root.split('/') for e_d in excl_dirs)]


def get_size(start_dir='.'):
    return sum(
        getsize(join(dpath, fname))
        for dpath, dnames, fnames in walk(start_dir) for fname in fnames)


class InsideDir(object):

    def __init__(self, dir_):
        self.dir = dir_
        self.old_dir = getcwd()

    def __enter__(self):
        chdir(self.dir)

    def __exit__(self, exc_type, exc_val, exc_tb):
        chdir(self.old_dir)


bld_dir = 'built/'
brd = {'master': 'dev', 'stable': 'stable'}
branch = brd[__get_branch()] if __get_branch() in brd else __get_branch()
ver = __get_version()
p3d_file = '{path}{name}-%s.p3d' % branch
win_file = '{path}{name}-%s-windows.exe' % branch
osx_file = '{path}{name}-%s-osx.zip' % branch
linux_file = '{path}{name}-%s-linux_{platform}' % branch
win_noint_file = '{path}{name}-%s-nointernet-windows.exe' % branch
osx_noint_file = '{path}{name}-%s-nointernet-osx.zip' % branch
linux_noint_file = '{path}{name}-%s-nointernet-linux_{platform}' % branch
src_file = '{path}{name}-%s-src.tar.gz' % branch
devinfo_file = '{path}{name}-%s-devinfo.tar.gz' % branch
test_file = '{path}{name}-%s-tests.tar.gz' % branch
docs_file = '{path}{name}-%s-docs.tar.gz' % branch
pdf_file = '{path}{name}-%s-code.tar.gz' % branch
extensions = ['txt', 'ttf', 'dds', 'egg', 'ogg', 'py', 'lua', 'rst', 'pdef',
              'mo', 'bam']
