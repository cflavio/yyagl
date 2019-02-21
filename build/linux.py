from os import remove, system, makedirs, walk, chdir
from os.path import basename, dirname, realpath, exists, abspath
from shutil import move, rmtree, copytree, copy
from glob import glob
from .build import ver, bld_dpath, branch, InsideDir, size
from .deployng import bld_ng


def bld_linux(target, source, env):
    ico_fpath = env['ICO_FPATH']
    bld_ng(env['APPNAME'], linux=True)
    start_dir = abspath('.') + '/'
    if exists(bld_dpath + 'linux'): rmtree(bld_dpath + 'linux')
    makedirs(bld_dpath + 'linux')
    with InsideDir(bld_dpath + 'linux'):
        __do_bld(start_dir, env['APPNAME'], ico_fpath)
    #rmtree(bld_dpath + 'linux')


def __do_bld(start_dir, appname, ico_fpath):
    __prepare(start_dir)
    __bld(appname, start_dir, ico_fpath)
    __bld_full_pkg(appname, ico_fpath)
    __bld_pckgs(appname)
    chdir('../..')
    #rmtree('dist')
    rmtree('build/__whl_cache__')
    rmtree('build/manylinux1_x86_64')
    rmtree('built/linux')


def __prepare(start_path):
    makedirs('img/data')
    curr_path = dirname(realpath(__file__)) + '/'
    copytree(curr_path + 'mojosetup/meta', 'img/meta')
    copytree(curr_path + 'mojosetup/scripts', 'img/scripts')
    copytree(curr_path + '../licenses', 'img/data/licenses')
    copy(start_path + 'license.txt', 'img/data/license.txt')
    copy(curr_path + 'mojosetup/mojosetup_amd64', '.')
    if not exists(curr_path + 'mojosetup/guis'): return
    makedirs('img/guis')
    libfpath = curr_path + 'mojosetup/guis/amd64/libmojosetupgui_gtkplus2.so'
    dst_dpath = 'img/guis/libmojosetupgui_gtkplus2.so'
    copy(libfpath, dst_dpath)


def __bld(appname, start_path, ico_fpath):
    arch = {'i386': 'i686', 'amd64': 'x86_64'}
    #system('tar -zxvf %s-0.0.0_manylinux1_x86_64.tar.xz' % (appname))
    #remove('.PKGINFO')
    copy('../../build/manylinux1_x86_64/' + appname, 'img/data/' + appname)
    copy(start_path + ico_fpath % '48', 'img/data/icon.png')
    seds = ['version', 'size', 'appname', 'AppName', 'vendorsite']
    sseds = ' '.join(["-e 's/<%s>/{%s}/'" % (sed, sed) for sed in seds])
    tmpl = 'sed -i.bak %s img/scripts/config.lua' % sseds
    cmd = tmpl.format(version=branch, size=size('img'),
                      appname=appname, AppName=appname.capitalize(),
                      vendorsite='ya2.it')
    system(cmd)


def __bld_full_pkg(appname, ico_fpath):
    #copytree('usr/lib/' + appname, 'img/data/lib')
    for fname in glob('../../build/manylinux1_x86_64/*.*'):
        copy(fname, 'img/data/')
    #remove('img/data/lib/panda3d/cmu_1.9/linux_%s/libstdc++.so.6' % platform)
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
    #tmpl = 'pdeploy -o  . {nointernet} -t host_dir=./lib ' + \
    #    '-t verify_contents=never -n {appname} -N {AppName} -v {version} ' + \
    #    '-a ya2.it -A "Ya2" -l "GPLv3" -L license.txt -e flavio@ya2.it ' + \
    #    '-t width=800 -t height=600 -P {platform} {icons} ../{p3d_fpath} ' + \
    #    'standalone'
    #dims = ['16', '32', '48', '128', '256']
    #ico_str = ''.join(["-i '" + ico_fpath % dim + "' " for dim in dims])
    #cmd = tmpl.format(
    #    path=bld_dpath, appname=appname, AppName=appname.capitalize(),
    #    version=ver, p3d_fpath=basename(p3d_fpath), platform='linux_'+platform,
    #    nointernet=nointernet, icons=ico_str)
    #system(cmd)
    #move('linux_' + platform + '/' + appname, 'img/data/' + appname)


def __bld_pckgs(appname):
    with InsideDir('img/data'): system('tar -cvf - * | xz > ../pdata.tar.xz')
    system('rm -rf img/data/*')
    move('img/pdata.tar.xz', 'img/data/pdata.tar.xz')
    with InsideDir('img'): system('zip -r ../pdata.zip *')
    system('cat pdata.zip >> ./mojosetup_amd64')
    fdst = '%s-%s-linux_amd64' % (appname, branch)
    move('mojosetup_amd64', fdst)
    system('chmod +x %s-%s-linux_amd64' % (appname, branch))
    fsrc = '%s-%s-linux_amd64' % (appname, branch)
    move(fsrc, '../%s-%s-linux_amd64' % (appname, branch))
