from os import system, remove, rename, chdir, makedirs, walk
from os.path import exists
from sys import executable
from shutil import rmtree, copytree, ignore_patterns, copy
from distutils.dir_util import copy_tree
from yyagl.build.build import InsideDir


prereq = '''psutil
bson
pyyaml
feedparser'''
requirements = '''
panda3d==1.10.4.1'''
excl_patterns = ['build/*', 'built/*', 'setup.py', 'requirements.txt', '*.swp',
                 'SConstruct', 'venv/*', '.git*', '*.pyc', 'options.yml',
                 '__pycache__']
plugins = ['pandagl', 'p3openal_audio']
setuppy = '''
from setuptools import setup
setup(name="%s", options=%s)'''


def bld_ng(appname, win=False, osx=False, linux=False):
    if exists('tmp_bld'): rmtree('tmp_bld')
    copytree('.', 'tmp_bld', ignore=ignore_patterns(
        '*.pyc', '*.pyd', 'tmp_bld', '*.egg', '.git*', 'built', 'dist',
        '.scons*', 'SCons*', 'README*', 'options*.yml', '*.po', '*.pot', '__pycache__', '*.pdf'))
    with InsideDir('tmp_bld'):
        copy_tree('../yyagl/licenses', './licenses')
        copy_tree('../licenses', './licenses')
        copy('../license.txt', './license.txt')
        for root, _, fnames in walk('./assets'):
            for _fname in fnames:
                fname = root + '/' + _fname
                is_track = 'assets/tracks/' in fname
                is_bam = fname.endswith('.bam')
                no_conv = ['/track_all', '/collision', 'Anim']
                is_no_conv = any(fname.endswith(concl + '.bam')
                                 for concl in no_conv)
                if is_track and is_bam and not is_no_conv:
                    remove(fname)
        tgts = ['win_amd64', 'macosx_10_6_x86_64', 'manylinux1_x86_64']
        dtgt = [win, osx, linux]
        deploy_platforms = [pl_str for (pl_str, is_pl) in zip(tgts, dtgt) if is_pl]
        opt_dct = {
            'build_apps': {
                'exclude_patterns': excl_patterns,
                'log_filename': '$USER_APPDATA/Yorg/p3d_log.log',
                'plugins': plugins,
                'gui_apps': {appname: 'main.py'},
                'icons': {appname: [
                    'assets/images/icon/icon256_png.png', 'assets/images/icon/icon128_png.png',
                    'assets/images/icon/icon48_png.png', 'assets/images/icon/icon32_png.png',
                    'assets/images/icon/icon16_png.png']},
                'include_patterns': [
                    '**/yyagl/licenses/*',
                    '**/licenses/*',
                    '**/*.bam',
                    '**/*.txo',
                    '**/*.yml',
                    '**/track_tr.py',
                    '**/*.txt',
                    '**/*.ttf',
                    '**/*.vert',
                    '**/*.frag',
                    '**/*.ogg',
                    '**/*.wav',
                    '**/*.mo'],
                'platforms': deploy_platforms,
                'include_modules': {'*': ['encodings.hex_codec']}},
            'bdist_apps': {
                'installers': {
                    'manylinux1_x86_64': ['xztar'],
                    'win_amd64': ['xztar', 'nsis'],
                    'macosx_10_6_x86_64': ['xztar']}}}
        with open('bsetup.py', 'w') as f_setup:
            f_setup.write(setuppy % (appname, opt_dct))
        with open('requirements.txt', 'w') as f_req:
            f_req.write(prereq)
        system('pip install -r requirements.txt')
        with open('requirements.txt', 'w') as f_req:
            f_req.write(requirements)
        system('pip install -r requirements.txt')
        system('python bsetup.py bdist_apps')  # we don't use executable but
                                               # venv's one
        list(map(remove, ['bsetup.py', 'requirements.txt']))
    copy_tree('tmp_bld/dist', 'dist')
    copy_tree('tmp_bld/build', 'build')
    rmtree('tmp_bld')
