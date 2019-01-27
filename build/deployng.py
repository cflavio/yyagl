from os import system, remove, rename, chdir
from os.path import exists
from sys import executable
from shutil import rmtree


prereq = '''psutil
bson
pyyaml
feedparser'''
requirements = '''
panda3d'''
excl_patterns = ['build/*', 'built/*', 'setup.py', 'requirements.txt', '*.swp',
                 'SConstruct', 'venv/*', '.git*', '*.pyc', 'options.yml']
incl_patterns = ['*.txo', '*.txt', '*.ttf', '*.bam', '*.vert', '*.frag', '*.yml']
plugins = ['pandagl', 'p3openal_audio']
setuppy = '''
from setuptools import setup
setup(name="%s", options=%s)'''


def bld_ng(appname, win=False, osx=False, linux=False):
    # system('pip install panda3d -i '
    #     'https://archive.panda3d.org/branches/deploy-ng --upgrade')
    if exists('build/__whl_cache__'):
        rmtree('build/__whl_cache__')
    tgts = ['win32', 'macosx_10_6_x86_64', 'manylinux1_x86_64']
    dtgt = [win, osx, linux]
    deploy_platforms = [pl_str for (pl_str, is_pl) in zip(tgts, dtgt) if is_pl]
    opt_dct = {
        'build_apps': {
            'exclude_patterns': excl_patterns,
            'include_patterns': incl_patterns,
            'log_filename': '$USER_APPDATA/Yorg/p3d_log.log',
            'plugins': plugins,
            'gui_apps': {appname: 'main.py'},
            'platforms': deploy_platforms,
            'include_modules': {'*': ['encodings.hex_codec']}},
        'bdist_apps': {
            'installers': {
                'manylinux1_x86_64': ['xztar'],
                'win32': ['xztar'],
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
