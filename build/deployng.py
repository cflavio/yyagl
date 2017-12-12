from os import system, remove
from os.path import exists
from sys import executable
from shutil import rmtree


prereq = '''
sleekxmpp==1.3.1
'''

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
            'include_patterns': incl_patterns,
            'plugins': plugins,
            'gui_apps': {appname + '_app': 'main.py'},
            'platforms': deploy_platforms}}
    with open('bsetup.py', 'w') as f_setup:
        f_setup.write(setuppy % (appname, opt_dct))
    with open('requirements.txt', 'w') as f_req:
        f_req.write(prereq)
    system('pip install -r requirements.txt')
    system('sed -i "/from xml.etree import cElementTree as ET/c\\from xml.etree import ElementTree as ET" venv/lib/python2.7/site-packages/sleekxmpp/xmlstream/stanzabase.py')
    system('''sed -i "/datetime\.strptime('1970-01-01 12:00:00', \\"%Y-%m-%d %H:%M:%S\\")/c\\#datetime\.strptime('1970-01-01 12:00:00', \\"%Y-%m-%d %H:%M:%S\\")" venv/lib/python2.7/site-packages/sleekxmpp/xmlstream/cert.py''')
    # NB only in virtualenv and only as a temporary workaround
    with open('requirements.txt', 'w') as f_req:
        f_req.write(requirements)
    system('python bsetup.py bdist_apps')  # we don't use executable but
                                           # venv's one
    map(remove, ['bsetup.py', 'requirements.txt'])
