from os import walk, chdir, getcwd, remove
from os.path import join, getsize
from subprocess import Popen, PIPE


bld_cmd = (
    'pdeploy -o  {dst_dir} {nointernet} -n {appname} -N {AppName} ' +
    '-v {version} -a ya2.it -A "Ya2" -l "GPLv3" -L license.txt ' +
    "-t width=800 -t height=600 -P {platform} -i '%s16_png.png' " +
    "-i '%s32_png.png' -i '%s48_png.png' -i '%s128_png.png' " +
    "-i '%s256_png.png' {p3d_fpath} installer") % (
        ('assets/images/icon/icon',) * 5)


def exec_cmd(cmd):
    ret = Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True).communicate()
    return '\n'.join(ret)


def __branch():
    return exec_cmd('git symbolic-ref HEAD').split('/')[-1].strip()


def __version():
    with open('assets/version.txt') as fver:
        return fver.read().strip() + '-' + exec_cmd('git rev-parse HEAD')[:7]


def img_tgt_names(files_):  # list of images' target filenames
    ext = lambda fname: 'png' if fname.endswith('_png.psd') else 'dds'
    return [fname[:fname.rfind('.') + 1] + ext(fname) for fname in files_]


def tracks_tgt_fnames():
    tr_root = 'assets/models/tracks/'
    for _, dnames, _ in walk(tr_root):
        return [tr_root + dname + '/track_all.bam' for dname in dnames]
    return []
    #return [tr_root + dname + '/track_all.bam' for _, dnames, _ in walk(tr_root) for dname in dnames]
    # this creates an empty folder assets/models/tracks/tex


def set_path(_bld_path):
    global bld_path
    bld_path = _bld_path + ('/' if not _bld_path.endswith('/') else '')
    return bld_path


def files(_extensions, excl_dirs=[]):
    return [join(root, fname)
            for root, _, fnames in walk('.')
            for fname in __files_ext(fnames, _extensions)
            if not any(e_d in root.split('/') for e_d in excl_dirs)]


def __files_ext(fnames, _extensions):
    return [fname for fname in fnames
            if any(fname.endswith('.' + ext) for ext in _extensions)]


def size(start_dir='.'):
    sizes = [getsize(join(root, fname))
             for root, _, fnames in walk(start_dir) for fname in fnames]
    return sum(sizes)


class TempFile(object):

    def __init__(self, fname, content):
        self.fname, self.content = fname, content

    def __enter__(self):
        with open(self.fname, 'w') as outfile:
            outfile.write(self.content)

    def __exit__(self, exc_type, exc_val, exc_tb):
        remove(self.fname)


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
branch = branch2ver[__branch()] if __branch() in branch2ver else __branch()
ver = __version()
p3d_fpath = '{dst_dir}{appname}-%s.p3d' % branch
win_fpath = '{dst_dir}{appname}-%s-windows.exe' % branch
osx_fpath = '{dst_dir}{appname}-%s-osx.zip' % branch
linux_fpath = '{dst_dir}{appname}-%s-linux_{platform}' % branch
win_noint_fpath = '{dst_dir}{appname}-%s-nointernet-windows.exe' % branch
osx_noint_fpath = '{dst_dir}{appname}-%s-nointernet-osx.zip' % branch
linux_noint_tmpl = '{dst_dir}{appname}-%s-nointernet-linux_{platform}'
linux_noint_fpath = linux_noint_tmpl % branch
src_fpath = '{dst_dir}{appname}-%s-src.tar.gz' % branch
devinfo_fpath = '{dst_dir}{appname}-%s-devinfo.tar.gz' % branch
test_fpath = '{dst_dir}{appname}-%s-tests.tar.gz' % branch
docs_fpath = '{dst_dir}{appname}-%s-docs.tar.gz' % branch
pdf_fpath = '{dst_dir}{appname}-%s-code.tar.gz' % branch
extensions = ['txt', 'ttf', 'dds', 'egg', 'ogg', 'py', 'lua', 'rst', 'pdef',
              'mo', 'bam']
