from os import walk, system, makedirs
from os.path import exists, abspath
from shutil import rmtree, move
from json import dumps
from yyagl.build.linux import _do_bld
from yyagl.build.deployng import bld_ng
from yyagl.build.build import bld_dpath, InsideDir


def bld_flatpak(target, source, env):  # unused target, source
    ico_fpath = env['ICO_FPATH']
    bld_ng(env['APPNAME'], linux=True)
    start_dir = abspath('.') + '/'
    if exists(bld_dpath + 'linux'): rmtree(bld_dpath + 'linux')
    makedirs(bld_dpath + 'linux')
    with InsideDir(bld_dpath + 'linux'):
        _do_bld(start_dir, env['APPNAME'], ico_fpath, False)
    with InsideDir(bld_dpath + 'linux/img/data'):
        system('tar -xvf pdata.tar.xz')
        __do_flatpak(env['FLATPAK_DST'], env['APPNAME'])
    # rmtree(bld_dpath + 'linux')
    rmtree('build/__whl_cache__')
    rmtree('build/manylinux1_x86_64')
    rmtree('built/linux')


def __do_flatpak(dst, name):
    files = []
    if exists('built'): rmtree('built')
    if exists('.flatpak-builder/build'): rmtree('.flatpak-builder/build')
    for root, _, files_ in walk('.'):
        if len(root.split('/')) == 1 or not root.split('/')[1].startswith('.'):
            for file_ in files_:
                if file_ != 'pdata.tar.xz' and not (
                        file_.startswith('options') and
                        file_.endswith('json')):
                    files += [root[2:] + ('/' if len(root) > 1 else '') +
                              file_]
    json = {
        'app-id': 'org.ya2.Yorg',
        'runtime': 'org.freedesktop.Platform',
        'runtime-version': '19.08',
        'sdk': 'org.freedesktop.Sdk',
        'command': 'yorg',
        'modules': [
            {'name': 'assets',
             'buildsystem': 'simple',
             'build-commands': ['install -d assets'],
             'sources': []},
            {'name': 'yorg',
             'buildsystem': 'simple',
             'build-commands': ['install -D yorg /app/bin/yorg'],
             'sources': [{'type': 'file', 'path': 'yorg'}]}],
        'finish-args': [
            '--socket=x11', '--share=network', '--share=ipc', '--device=dri']}
    for file_ in files:
        enc_file = file_.replace('/', '____')
        cmd = 'install -D "%s" "/app/bin/%s"' % (enc_file, file_)
        json['modules'][0]['build-commands'] += [cmd]
        json['modules'][0]['sources'] += [
            {'type': 'file', 'path': file_, 'dest-filename': enc_file}]
    import pprint; pprint.pprint(json)
    with open('org.ya2.Yorg.json', 'w') as fjson: fjson.write(dumps(json))
    repo_name = 'flatpak_' + name + '_repo'
    test_name = 'flatpak_' + name + '_test'
    system('flatpak-builder %s org.ya2.Yorg.json' % test_name)
    # flatpak-builder --run built/flatpak_yorg_test built/org.ya2.Yorg.json yorg
    system('flatpak-builder --repo=%s --force-clean --disable-rofiles-fuse '
           'built org.ya2.Yorg.json' % repo_name)
    move('org.ya2.Yorg.json', dst + '/org.ya2.Yorg.json')
    move(repo_name, dst + '/' + repo_name)
    move(test_name, dst + '/' + test_name)
    # flatpak --user remote-add --no-gpg-verify yorg_repo built/flatpak_yorg_repo
    # flatpak --user install yorg_repo org.ya2.Yorg
    # flatpak run org.ya2.Yorg
