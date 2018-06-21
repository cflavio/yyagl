from os import remove, system, makedirs, walk
from os.path import basename, dirname, realpath, exists, abspath
from shutil import move, rmtree, copytree, copy
from .build import ver, bld_dpath, branch, InsideDir, size, \
    bld_cmd
from .deployng import bld_ng


def bld_linux(target, source, env):
    if env['DEPLOYNG']:
        bld_ng(env['APPNAME'], linux_32=env['PLATFORM'] == 'i386',
               linux_64=env['PLATFORM'] == 'amd64')
        return
    ico_fpath = env['ICO_FPATH']
    nointernet = '-s' if env['NOINTERNET'] else ''
    int_str = '-nointernet' if env['NOINTERNET'] else ''
    p3d_fpath = env['P3D_PATH'][:-4] + 'nopygame.p3d'
    cmd = bld_cmd.format(
        dst_dir=bld_dpath, appname=env['APPNAME'],
        AppName=env['APPNAME'].capitalize(), version=ver, p3d_fpath=p3d_fpath,
        platform='linux_' + env['PLATFORM'], nointernet=nointernet)
    system(cmd)
    start_dir = abspath('.') + '/'
    with InsideDir(bld_dpath + 'linux_' + env['PLATFORM']):
        __do_bld(start_dir, env['APPNAME'], env['PLATFORM'], ico_fpath,
                 nointernet, p3d_fpath, int_str)
    rmtree(bld_dpath + 'linux_' + env['PLATFORM'])


def __do_bld(start_dir, appname, platform, ico_fpath, nointernet, p3d_fpath,
             int_str):
    __prepare(start_dir, platform)
    __bld(appname, start_dir, platform, ico_fpath)
    if nointernet:
        __bld_full_pkg(appname, platform, ico_fpath, p3d_fpath, nointernet)
    __bld_pckgs(appname, platform, int_str)


def __prepare(start_path, platform):
    makedirs('img/data')
    curr_path = dirname(realpath(__file__)) + '/'
    copytree(curr_path + 'mojosetup/meta', 'img/meta')
    copytree(curr_path + 'mojosetup/scripts', 'img/scripts')
    copytree(curr_path + '../licenses', 'img/data/licenses')
    copy(start_path + 'license.txt', 'img/data/license.txt')
    copy(curr_path + 'mojosetup/mojosetup_' + platform, '.')
    if not exists(curr_path + 'mojosetup/guis'): return
    makedirs('img/guis')
    libfpath = curr_path + 'mojosetup/guis/%s/libmojosetupgui_gtkplus2.so'
    dst_dpath = 'img/guis/libmojosetupgui_gtkplus2.so'
    copy(libfpath % platform, dst_dpath)


def __bld(appname, start_path, platform, ico_fpath):
    arch = {'i386': 'i686', 'amd64': 'x86_64'}
    system('tar -zxvf %s-%s-1-%s.pkg.tar.gz' % (appname, ver, arch[platform]))
    remove('.PKGINFO')
    move('usr/bin/' + appname, 'img/data/' + appname)
    copy(start_path + ico_fpath % '48', 'img/data/icon.png')
    seds = ['version', 'size', 'appname', 'AppName', 'vendorsite']
    sseds = ' '.join(["-e 's/<%s>/{%s}/'" % (sed, sed) for sed in seds])
    tmpl = 'sed -i.bak %s img/scripts/config.lua' % sseds
    cmd = tmpl.format(version=branch, size=size('img'),
                      appname=appname, AppName=appname.capitalize(),
                      vendorsite='ya2.it')
    system(cmd)


def __bld_full_pkg(appname, platform, ico_fpath, p3d_fpath, nointernet):
    copytree('usr/lib/' + appname, 'img/data/lib')
    copytree('../../assets', 'img/data/assets')
    copytree('../../yyagl/assets', 'img/data/yyagl/assets')
    for root, _, fnames in walk('img/data/assets'):
        for fname in fnames:
            fpath = root + '/' + fname
            rm_ext = ['psd', 'po', 'pot', 'egg']
            if any(fpath.endswith('.' + ext) for ext in rm_ext):
                remove(fpath)
            if any(fpath.endswith('.' + ext) for ext in ['png', 'jpg']):
                remove(fpath)
            if 'assets/models/tracks/' in fpath and \
                    fpath.endswith('.bam') and not \
                    any(fpath.endswith(concl + '.bam')
                            for concl in ['/track_all', '/collision', 'Anim']):
                remove(fpath)
    tmpl = 'pdeploy -o  . {nointernet} -t host_dir=./lib ' + \
        '-t verify_contents=never -n {appname} -N {AppName} -v {version} ' + \
        '-a ya2.it -A "Ya2" -l "GPLv3" -L license.txt -e flavio@ya2.it ' + \
        '-t width=800 -t height=600 -P {platform} {icons} ../{p3d_fpath} ' + \
        'standalone'
    dims = ['16', '32', '48', '128', '256']
    ico_str = ''.join(["-i '" + ico_fpath % dim + "' " for dim in dims])
    cmd = tmpl.format(
        path=bld_dpath, appname=appname, AppName=appname.capitalize(),
        version=ver, p3d_fpath=basename(p3d_fpath), platform='linux_'+platform,
        nointernet=nointernet, icons=ico_str)
    system(cmd)
    move('linux_' + platform + '/' + appname, 'img/data/' + appname)


def __bld_pckgs(appname, platform, int_str):
    with InsideDir('img/data'): system('tar -cvf - * | xz > ../pdata.tar.xz')
    system('rm -rf img/data/*')
    move('img/pdata.tar.xz', 'img/data/pdata.tar.xz')
    with InsideDir('img'): system('zip -r ../pdata.zip *')
    system('cat pdata.zip >> ./mojosetup_' + platform)
    fdst = '%s-%s%s-linux_%s' % (appname, branch, int_str, platform)
    move('mojosetup_' + platform, fdst)
    system('chmod +x %s-%s%s-linux_%s' % (appname, branch, int_str, platform))
    fsrc = '%s-%s%s-linux_%s' % (appname, branch, int_str, platform)
    move(fsrc, '../%s-%s%s-linux_%s' % (appname, branch, int_str, platform))
