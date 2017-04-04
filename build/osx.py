from os import system, walk, remove
from shutil import rmtree, copytree
from .build import ver, path, ver_branch, bld_cmd


def build_osx(target, source, env):
    nointernet = '-s' if env['NOINTERNET'] else ''
    int_str = '-nointernet' if env['NOINTERNET'] else ''
    build_command = bld_cmd(env['SUPERMIRROR']).format(
        path=path, name=env['NAME'], Name=env['NAME'].capitalize(),
        version=ver, p3d_path=env['P3D_PATH'][:-4] + 'nopygame.p3d',
        platform='osx_i386', nointernet=nointernet)
    system(build_command)
    appname = env['NAME'].capitalize()
    copytree('assets', path + 'osx_i386/%s.app/Contents/MacOS/assets' % appname)
    copytree('yyagl/assets', path + 'osx_i386/%s.app/Contents/MacOS/yyagl/assets' % appname)
    for root, dirnames, filenames in walk(path + 'osx_i386/%s.app/Contents/MacOS/assets' % appname):
        for filename in filenames:
            fname = root + '/' + filename
            if any(fname.endswith('.' + ext) for ext in ['psd', 'po', 'pot', 'egg']):
                remove(fname)
            if 'assets/models/tracks/' in fname and fname.endswith('.bam') and \
                    not any(fname.endswith(concl + '.bam') for concl in ['/track', '/collision', 'Anim']):
                remove(fname)
    osx_path = '{Name}.app'
    osx_tgt = '{name}-{version}{int_str}-osx.zip'
    osx_cmd_tmpl = 'cd ' + path + 'osx_i386 && zip -r ../' + osx_tgt + ' ' + \
        osx_path + ' && cd ../..'
    osx_cmd = osx_cmd_tmpl.format(
        Name=env['NAME'].capitalize(), name=env['NAME'], version=ver_branch,
        int_str=int_str)
    system(osx_cmd)
    rmtree('%sosx_i386' % path)
