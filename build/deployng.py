from os import system, remove
from os.path import exists
from sys import executable
from shutil import rmtree


requirements = '''
--extra-index-url https://archive.panda3d.org/branches/deploy-ng/
--pre
panda3d==1.10.0.dev1129+g55ce23f'''


excl_paths = ['build/*', 'built/*', 'setup.py', 'requirements.txt', '*.swp',
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
            'copy_paths': ['.'],
            'exclude_paths': excl_paths,
            'gui_apps': {appname + '_app': 'main.py'},
            'deploy_platforms': deploy_platforms}}
    with open('setup.py', 'w') as f_setup:
        f_setup.write(setuppy % (appname, opt_dct))
    with open('requirements.txt', 'w') as f_req:
        f_req.write(requirements)
    system(executable + ' setup.py bdist_apps')
    map(remove, ['setup.py', 'requirements.txt'])
