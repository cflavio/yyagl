from os import system, remove
from os.path import exists
from sys import executable
from shutil import rmtree


requirements = '''
--extra-index-url https://archive.panda3d.org/branches/deploy-ng/
--pre panda3d'''


excl_patterns = ['build/*', 'built/*', 'setup.py', 'requirements.txt', '*.swp',
              'SConstruct', 'venv/*', '.git*', '*.pyc']


setuppy = '''
from setuptools import setup
setup(name="%s", options=%s)'''


def bld_ng(appname, win=False, osx=False, linux_32=False, linux_64=False):
    # system('pip install panda3 -i '
    #     'https://archive.panda3d.org/branches/deploy-ng --upgrade')
    if exists('build/__whl_cache__'):
        rmtree('build/__whl_cache__')
    tgts = ['win32', 'macosx_10_6_x86_64', 'manylinux1_x86',
            'manylinux1_x86_64']
    dtgt = [win, osx, linux_32, linux_64]
    deploy_platforms = [pl_str for (pl_str, is_pl) in zip(tgts, dtgt) if is_pl]
    opt_dct = {
        'build_apps': {
            'exclude_patterns': excl_patterns,
            'gui_apps': {appname + '_app': 'main.py'},
            'platforms': deploy_platforms}}
    with open('bsetup.py', 'w') as f_setup:
        f_setup.write(setuppy % (appname, opt_dct))
    with open('requirements.txt', 'w') as f_req:
        f_req.write(requirements)
    system(executable + ' bsetup.py bdist_apps')
    map(remove, ['bsetup.py', 'requirements.txt'])
