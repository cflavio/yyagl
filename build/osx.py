from os import system, walk, remove
from shutil import rmtree, copytree
from .build import ver, bld_dpath, branch, bld_cmd
from .deployng import bld_ng


def bld_osx(target, source, env):
    if env['DEPLOYNG']:
        bld_ng(env['APPNAME'], osx=True)
        return
    nointernet = '-s' if env['NOINTERNET'] else ''
    internet_str = '-nointernet' if env['NOINTERNET'] else ''
    cmd = bld_cmd.format(
        dst_dir=bld_dpath, appname=env['APPNAME'],
        AppName=env['APPNAME'].capitalize(), version=ver,
        p3d_fpath=env['P3D_PATH'][:-4] + 'nopygame.p3d', platform='osx_i386',
        nointernet=nointernet)
    system(cmd)
    appname = env['APPNAME'].capitalize()
    pmacos = 'osx_i386/%s.app/Contents/MacOS/' % appname
    copytree('assets', bld_dpath + pmacos + 'assets')
    copytree('yyagl/assets', bld_dpath + pmacos + 'yyagl/assets')
    for root, _, fnames in walk(bld_dpath + pmacos + 'assets'):
        for _fname in fnames:
            fname = root + '/' + _fname
            rm_ext = ['psd', 'po', 'pot', 'egg']
            if any(fname.endswith('.' + ext) for ext in rm_ext):
                remove(fname)
            rm_ext = ['png', 'jpg']
            is_mod = 'assets/models/' in fname
            if is_mod and any(fname.endswith('.' + ext) for ext in rm_ext):
                remove(fname)
            is_track = 'assets/models/tracks/' in fname
            is_bam = fname.endswith('.bam')
            no_conv = ['/track_all', '/collision', 'Anim']
            is_no_conv = any(fname.endswith(con + '.bam') for con in no_conv)
            if is_track and is_bam and not is_no_conv:
                remove(fname)
    fname = '{AppName}.app'
    pkg = '{appname}-{version}{internet_str}-osx.zip'
    tmpl_args = (bld_dpath, pkg, fname)
    tmpl = 'cd %sosx_i386 && zip -r ../%s %s && cd ../..' % tmpl_args
    cmd = tmpl.format(
        AppName=env['APPNAME'].capitalize(), appname=env['APPNAME'],
        version=branch, internet_str=internet_str)
    system(cmd)
    rmtree('%sosx_i386' % bld_dpath)
