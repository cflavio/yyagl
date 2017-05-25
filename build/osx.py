from os import system, walk, remove
from shutil import rmtree, copytree
from .build import ver, bld_dpath, branch, bld_cmd
from .deployng import build_ng


def build_osx(target, source, env):
    if env['NG']:
        build_ng(env['APPNAME'], osx=True)
        return
    nointernet = '-s' if env['NOINTERNET'] else ''
    internet_str = '-nointernet' if env['NOINTERNET'] else ''
    build_cmd = bld_cmd.format(
        path=bld_dpath, name=env['APPNAME'], Name=env['APPNAME'].capitalize(),
        version=ver, p3d_path=env['P3D_PATH'][:-4] + 'nopygame.p3d',
        platform='osx_i386', nointernet=nointernet)
    system(build_cmd)
    appname = env['APPNAME'].capitalize()
    tgt = bld_dpath + 'osx_i386/%s.app/Contents/MacOS/assets' % appname
    copytree('assets', tgt)
    tgt = bld_dpath + 'osx_i386/%s.app/Contents/MacOS/yyagl/assets' % appname
    copytree('yyagl/assets', tgt)
    start_dir = bld_dpath + 'osx_i386/%s.app/Contents/MacOS/assets' % appname
    for root, _, filenames in walk(start_dir):
        for filename in filenames:
            fname = root + '/' + filename
            del_ext = ['psd', 'po', 'pot', 'egg']
            if any(fname.endswith('.' + ext) for ext in del_ext):
                remove(fname)
            rm_ext = ['png', 'jpg']
            if 'assets/models/' in fname and any(fname.endswith('.' + ext) for ext in rm_ext):
                remove(fname)
            if 'assets/models/tracks/' in fname and fname.endswith('.bam') \
                    and not any(fname.endswith(concl + '.bam')
                                for concl in ['/track_all', '/collision', 'Anim']):
                remove(fname)
    osx_fname = '{Name}.app'
    osx_pkg = '{name}-{version}{internet_str}-osx.zip'
    osx_cmd_tmpl = 'cd ' + bld_dpath + 'osx_i386 && zip -r ../' + osx_pkg + \
        ' ' + osx_fname + ' && cd ../..'
    osx_cmd = osx_cmd_tmpl.format(
        Name=env['APPNAME'].capitalize(), name=env['APPNAME'], version=branch,
        internet_str=internet_str)
    system(osx_cmd)
    rmtree('%sosx_i386' % bld_dir)
