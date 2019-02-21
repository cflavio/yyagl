from os import system, walk, remove
from shutil import rmtree, copytree, move
from .build import ver, bld_dpath, branch
from .deployng import bld_ng


def bld_osx(target, source, env):
    #if env['DEPLOYNG']:
    #    bld_ng(env['APPNAME'], osx=True)
    #    return
    #nointernet = '-s' if env['NOINTERNET'] else ''
    #internet_str = '-nointernet' if env['NOINTERNET'] else ''
    #cmd = bld_cmd.format(
    #    dst_dir=bld_dpath, appname=env['APPNAME'],
    #    AppName=env['APPNAME'].capitalize(), version=ver,
    #    p3d_fpath=env['P3D_PATH'][:-4] + 'nopygame.p3d', platform='osx_i386',
    #    nointernet=nointernet)
    #system(cmd)
    bld_ng(env['APPNAME'], osx=True)
    appname = env['APPNAME'].capitalize()
    pmacos = '../build/macosx_10_6_x86_64/%s.app/Contents/MacOS/' % appname.lower()
    copytree('assets', bld_dpath + pmacos + 'assets')
    copytree('yyagl/assets', bld_dpath + pmacos + 'yyagl/assets')
    for root, _, fnames in walk(bld_dpath + pmacos + 'assets'):
        for _fname in fnames:
            fname = root + '/' + _fname
            rm_ext = ['psd', 'po', 'pot', 'egg']
            if any(fname.endswith('.' + ext) for ext in rm_ext):
                remove(fname)
            if any(fname.endswith('.' + ext) for ext in ['png', 'jpg']):
                remove(fname)
            is_track = 'assets/models/tracks/' in fname
            is_bam = fname.endswith('.bam')
            no_conv = ['/track_all', '/collision', 'Anim']
            is_no_conv = any(fname.endswith(con + '.bam') for con in no_conv)
            if is_track and is_bam and not is_no_conv:
                remove(fname)
    fname = '{AppName}.app'
    pkg = '{appname}-{version}-osx.tar.xz'
    tmpl_args = (bld_dpath + '../build/', fname, pkg)
    tmpl = 'cd %smacosx_10_6_x86_64 && tar -cv %s | xz > ../%s && cd ../..' % tmpl_args
    cmd = tmpl.format(
        AppName=env['APPNAME'].lower(), appname=env['APPNAME'],
        version=branch)
    system(cmd)
    src = '{dst_dir}../build/{appname}-{version}-osx.tar.xz'
    tgt_file = '{dst_dir}{appname}-{version}-osx.tar.xz'
    src_fmt = src.format(dst_dir=bld_dpath, appname=env['APPNAME'],
                         version=branch)
    tgt_fmt = tgt_file.format(dst_dir=bld_dpath, appname=env['APPNAME'],
                              version=branch)
    move(src_fmt, tgt_fmt)
    #rmtree('dist')
    rmtree('build/__whl_cache__')
    rmtree('build/macosx_10_6_x86_64')
