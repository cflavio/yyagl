from os import system, makedirs, chmod, stat, remove
from os.path import exists, abspath
from shutil import rmtree, copy, copytree
from urllib.request import urlretrieve
from stat import S_IEXEC
from yyagl.build.linux import _do_bld
from yyagl.build.deployng import bld_ng
from yyagl.build.build import bld_dpath, InsideDir, linux_fpath


def bld_appimage(target, source, env):  # unused target, source
    ico_fpath = env['ICO_FPATH']
    bld_ng(env['APPNAME'], linux=True)
    start_dir = abspath('.') + '/'
    if exists(bld_dpath + 'linux'): rmtree(bld_dpath + 'linux')
    makedirs(bld_dpath + 'linux')
    with InsideDir(bld_dpath + 'linux'):
        _do_bld(start_dir, env['APPNAME'], ico_fpath, False)
    with InsideDir(bld_dpath + 'linux/img/data'):
        system('tar -xvf pdata.tar.xz')
    __do_appimage(env['APPNAME'])
    # #rmtree(bld_dpath + 'linux')
    # rmtree('build/__whl_cache__')
    # rmtree('build/manylinux1_x86_64')
    rmtree('built/linux')
    rmtree('built/' + env['APPNAME'].capitalize() + '.AppDir')
    remove('built/appimagetool-x86_64.AppImage')
    remove(linux_fpath.format(
        dst_dir='built/', appname=env['APPNAME']) + '_amd64')


appruncontent = '''#!/bin/sh
SELF=$(readlink -f "$0")
HERE=${SELF%/*}
export PATH="${HERE}/usr/bin/:${HERE}/usr/sbin/:${HERE}/usr/games/:${HERE}/bin/:${HERE}/sbin/${PATH:+:$PATH}"
export LD_LIBRARY_PATH="${HERE}/usr/bin/:${HERE}/usr/lib/:${HERE}/usr/lib/i386-linux-gnu/:${HERE}/usr/lib/x86_64-linux-gnu/:${HERE}/usr/lib32/:${HERE}/usr/lib64/:${HERE}/lib/:${HERE}/lib/i386-linux-gnu/:${HERE}/lib/x86_64-linux-gnu/:${HERE}/lib32/:${HERE}/lib64/${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
export PYTHONPATH="${HERE}/usr/bin/:${HERE}/usr/share/pyshared/${PYTHONPATH:+:$PYTHONPATH}"
export XDG_DATA_DIRS="${HERE}/usr/share/${XDG_DATA_DIRS:+:$XDG_DATA_DIRS}"
export PERLLIB="${HERE}/usr/share/perl5/:${HERE}/usr/lib/perl5/${PERLLIB:+:$PERLLIB}"
export GSETTINGS_SCHEMA_DIR="${HERE}/usr/share/glib-2.0/schemas/${GSETTINGS_SCHEMA_DIR:+:$GSETTINGS_SCHEMA_DIR}"
export QT_PLUGIN_PATH="${HERE}/usr/lib/qt4/plugins/:${HERE}/usr/lib/i386-linux-gnu/qt4/plugins/:${HERE}/usr/lib/x86_64-linux-gnu/qt4/plugins/:${HERE}/usr/lib32/qt4/plugins/:${HERE}/usr/lib64/qt4/plugins/:${HERE}/usr/lib/qt5/plugins/:${HERE}/usr/lib/i386-linux-gnu/qt5/plugins/:${HERE}/usr/lib/x86_64-linux-gnu/qt5/plugins/:${HERE}/usr/lib32/qt5/plugins/:${HERE}/usr/lib64/qt5/plugins/${QT_PLUGIN_PATH:+:$QT_PLUGIN_PATH}"
EXEC=$(grep -e '^Exec=.*' "${HERE}"/*.desktop | head -n 1 | cut -d "=" -f 2 | cut -d " " -f 1)
exec "${EXEC}" "$@"'''

desktopcontent = '''[Desktop Entry]
Name=Yorg
Exec=yorg
Icon=icon
Type=Application
Categories=Game;'''


def __do_appimage(name):
    with InsideDir(bld_dpath):
        dirname = name.capitalize() + '.AppDir'
        if exists(dirname): rmtree(dirname)
        makedirs(dirname)
    with InsideDir(bld_dpath + '/' + name.capitalize() + '.AppDir'):
        with open('AppRun', 'w') as f_apprun: f_apprun.write(appruncontent)
        _stat = stat('AppRun')
        chmod('AppRun', _stat.st_mode | S_IEXEC)
        with open(name + '.desktop', 'w') as fdesktop:
            fdesktop.write(desktopcontent)
        copy('../../assets/images/icon/icon256_png.png', './icon.png')
        copytree('../linux/img/data', './usr/bin')
    with InsideDir(bld_dpath):
        urlretrieve('https://github.com/AppImage/AppImageKit/releases/download'
                    '/12/appimagetool-x86_64.AppImage',
                    'appimagetool-x86_64.AppImage')
        _stat = stat('appimagetool-x86_64.AppImage')
        chmod('appimagetool-x86_64.AppImage', _stat.st_mode | S_IEXEC)
        system('./appimagetool-x86_64.AppImage ' + name.capitalize() +
               '.AppDir')

#     files = []
#     if exists('built'): rmtree('built')
#     if exists('.flatpak-builder/build'): rmtree('.flatpak-builder/build')
#     for root, _, files_ in walk('.'):
#         if len(root.split('/')) == 1 or not \
#                 root.split('/')[1].startswith('.'):
#             for file_ in files_:
#                 if file_ != 'pdata.tar.xz' and not (
#                         file_.startswith('options') and
#                         file_.endswith('json')):
#                     files += [root[2:] + ('/' if len(root) > 1 else '') +
#                               file_]
#     json = {
#         'app-id': 'org.ya2.Yorg',
#         'runtime': 'org.freedesktop.Platform',
#         'runtime-version': '18.08',
#         'sdk': 'org.freedesktop.Sdk',
#         'command': 'yorg',
#         'modules': [
#             {'name': 'assets',
#              'buildsystem': 'simple',
#              'build-commands': ['install -d assets'],
#              'sources': []},
#             {'name': 'yorg',
#              'buildsystem': 'simple',
#              'build-commands': ['install -D yorg /app/bin/yorg'],
#               'sources': [{'type': 'file', 'path': 'yorg'}]}],
#         'finish-args': [
#            '--socket=x11', '--share=network', '--share=ipc', '--device=dri']}
#     for file_ in files:
#         enc_file = file_.replace('/', '____')
#         cmd = 'install -D "%s" "/app/bin/%s"' % (enc_file, file_)
#         json['modules'][0]['build-commands'] += [cmd]
#         json['modules'][0]['sources'] += [
#             {'type': 'file', 'path': file_, 'dest-filename': enc_file}]
#     import pprint; pprint.pprint(json)
#     with open('org.ya2.Yorg.json', 'w') as f: f.write(dumps(json))
#     repo_name = 'flatpak_' + name + '_repo'
#     system('flatpak-builder --repo=%s --force-clean --disable-rofiles-fuse '
#            'built org.ya2.Yorg.json' % repo_name)
#     move(repo_name, dst)
#     #flatpak-builder --run build-dir org.flatpak.Hello.json hello.sh
