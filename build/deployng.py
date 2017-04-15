from os import system, remove


requirements = '''
--extra-index-url https://panda3d-pypi.stokescloud.ddns.net/
--pre
panda3d'''


exclude_paths = ['build/*', 'built/*', 'setup.py', 'requirements.txt', '*.swp',
                 'SConstruct', 'venv/*', '.git*', '*.pyc']

setuppy = '''
from setuptools import setup
setup(name="%s", options=%s)'''

def build_ng(appname, win=False, osx=False, linux_32=False, linux_64=False):
    deploy_platforms = []
    if win:
        deploy_platforms += ['win32']
    if osx:
        deploy_platforms += ['macosx_10_6_x86_64']
    if linux_32:
        deploy_platforms += ['manylinux1_x86']
    if linux_64:
        deploy_platforms += ['manylinux1_x86_64']
    options_dct = {
        'build_apps': {
            'copy_paths': ['.'],
            'exclude_paths': exclude_paths,
            'gui_apps': {appname + '_app': 'main.py'},
            'deploy_platforms': deploy_platforms}}
    with open('setup.py', 'w') as f:
        f.write(setuppy % (appname, options_dct))
    with open('requirements.txt', 'w') as f:
        f.write(requirements)
    system('python setup.py bdist_apps')
    map(remove, ['setup.py', 'requirements.txt'])
