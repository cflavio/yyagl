from os import system, remove, rename, chdir
from os.path import exists
from sys import executable
from shutil import rmtree


prereq = '''psutil
simpleubjson
pyyaml
feedparser'''
requirements = '''
--pre --extra-index-url https://archive.panda3d.org/branches/deploy-ng
panda3d'''
excl_patterns = ['build/*', 'built/*', 'setup.py', 'requirements.txt', '*.swp',
                 'SConstruct', 'venv/*', '.git*', '*.pyc', 'options.yml']
incl_patterns = ['*.txo', '*.txt', '*.ttf', '*.bam', '*.vert', '*.frag', '*.yml']
plugins = ['pandagl', 'p3openal_audio']
setuppy = '''
from setuptools import setup
setup(name="%s", options=%s)'''


def bld_ng(appname, win=False, osx=False, linux_32=False, linux_64=False):
    # system('pip install panda3d -i '
    #     'https://archive.panda3d.org/branches/deploy-ng --upgrade')
    if exists('build/__whl_cache__'):
        rmtree('build/__whl_cache__')
    tgts = ['win32', 'macosx_10_6_x86_64', 'manylinux1_i686',
            'manylinux1_x86_64']
    dtgt = [win, osx, linux_32, linux_64]
    deploy_platforms = [pl_str for (pl_str, is_pl) in zip(tgts, dtgt) if is_pl]
    opt_dct = {
        'build_apps': {
            'exclude_patterns': excl_patterns,
            'include_patterns': incl_patterns,
            'log_filename': '$USER_APPDATA/Yorg/p3d_log.log',
            'plugins': plugins,
            'console_apps': {appname: 'main.py'},
            'platforms': deploy_platforms,
            'include_modules': {'*': ['encodings.hex_codec']}},
        'bdist_apps': {
            'installers': {
                'manylinux1_x86_64': ['gztar'],  # xztar isn't supported in py2
                'manylinux1_i386': ['gztar'],  # xztar isn't supported in py2
                'win32': ['gztar'],  # xztar isn't supported in py2
                'macosx_10_6_x86_64': ['gztar']}}}  # xztar isn't supported in py2
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
    map(remove, ['bsetup.py', 'requirements.txt'])
    chdir('build')
    # we need the following since xztar archives aren't supported in py2
    for platf in deploy_platforms:
        platf2desc = {
            'win32': 'windows',
            'macosx_10_6_x86_64': 'osx',
            'manylinux1_i686': 'linux_32',
            'manylinux1_x86_64': 'linux_64'}
        desc = platf2desc[platf]
        rename(platf, 'yorg')
        system('tar cfJ yorg-ng-%s.tar.xz yorg' % desc)
        rmtree('yorg')
        remove('yorg-0.0.0_%s.tar.gz' % platf)
    rmtree('__whl_cache__')
    chdir('..')
