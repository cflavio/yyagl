from os import remove, system, makedirs, walk
from os.path import basename, dirname, realpath, exists, abspath
from shutil import move, rmtree, copytree, copy
from .build import ver, bld_dir, branch, InsideDir, get_size, \
    bld_cmd
from .deployng import build_ng


def build_linux(target, source, env):
    if env['NG']:
        build_ng(env['APPNAME'], linux_64=True)
        return
    ico_file = env['ICO_FILE']
    nointernet = '-s' if env['NOINTERNET'] else ''
    int_str = '-nointernet' if env['NOINTERNET'] else ''
    p3d_path = env['P3D_PATH'][:-4] + 'nopygame.p3d'
    bld_command = bld_cmd.format(
        path=bld_dir, name=env['APPNAME'], Name=env['APPNAME'].capitalize(),
        version=ver, p3d_path=p3d_path, platform='linux_'+env['PLATFORM'],
        nointernet=nointernet)
    system(bld_command)
    start_dir = abspath('.') + '/'
    with InsideDir(bld_dir + 'linux_' + env['PLATFORM']):
        __prepare(start_dir, env['PLATFORM'])
        __bld(env['APPNAME'], start_dir, env['PLATFORM'], ico_file)
        if nointernet:
            __bld_full_pkg(env['APPNAME'], env['PLATFORM'], ico_file, p3d_path,
                           nointernet)
        __bld_packages(env['APPNAME'], env['PLATFORM'], int_str)
    rmtree(bld_dir + 'linux_' + env['PLATFORM'])


def __prepare(start_dir, platform):
    makedirs('img/data')
    curr_dir = dirname(realpath(__file__)) + '/'
    copytree(curr_dir + 'mojosetup/meta', 'img/meta')
    copytree(curr_dir + 'mojosetup/scripts', 'img/scripts')
    copytree(curr_dir + '../licenses', 'img/data/licenses')
    copy(start_dir + 'license.txt', 'img/data/license.txt')
    copy(curr_dir + 'mojosetup/mojosetup_' + platform, '.')
    if not exists(curr_dir + 'mojosetup/guis'):
        return
    makedirs('img/guis')
    libpath = curr_dir + 'mojosetup/guis/%s/libmojosetupgui_gtkplus2.so'
    dst_path = 'img/guis/libmojosetupgui_gtkplus2.so'
    copy(start_dir + libpath % platform, dst_path)


def __bld(appname, start_dir, platform, ico_file):
    arch_dict = {'i386': 'i686', 'amd64': 'x86_64'}
    cmd_tmpl = 'tar -zxvf %s-%s-1-%s.pkg.tar.gz'
    system(cmd_tmpl % (appname, ver, arch_dict[platform]))
    remove('.PKGINFO')
    move('usr/bin/' + appname, 'img/data/' + appname)
    copy(start_dir + ico_file % '48', 'img/data/icon.png')
    seds = ['version', 'size', 'appname', 'AppName']
    seds = ' '.join(["-e 's/<%s>/{%s}/'" % (sed, sed) for sed in seds])
    cmd_tmpl = 'sed -i.bak %s img/scripts/config.lua' % seds
    cmd = cmd_tmpl.format(version=branch, size=get_size('img'),
                          appname=appname, AppName=appname.capitalize())
    system(cmd)


def __bld_full_pkg(name, platform, ico_file, p3d_path, nointernet):
    copytree('usr/lib/'+name, 'img/data/lib')
    copytree('../../assets', 'img/data/assets')
    copytree('../../yyagl/assets', 'img/data/yyagl/assets')
    for root, _, filenames in walk('img/data/assets'):
        for filename in filenames:
            fname = root + '/' + filename
            rm_ext = ['psd', 'po', 'pot', 'egg']
            if any(fname.endswith('.' + ext) for ext in rm_ext):
                remove(fname)
            if fname.startswith('assets/models/tracks/') and \
                    fname.endswith('.bam') and not \
                    any(fname.endswith(concl + '.bam')
                        for concl in ['/track', '/collision', 'Anim']):
                remove(fname)
    cmd_tmpl = 'pdeploy -o  . {nointernet} -t host_dir=./lib ' + \
        '-t verify_contents=never -n {name} -N {Name} -v {version} ' + \
        '-a ya2.it -A "Ya2" -l "GPLv3" -L license.txt -e flavio@ya2.it ' + \
        '-t width=800 -t height=600 -P {platform} {icons} ../{p3d_path} ' + \
        'standalone'
    dims = ['16', '32', '48', '128', '256']
    ico_str = ''.join(["-i '" + ico_file % dim + "' " for dim in dims])
    cmd = cmd_tmpl.format(
        path=bld_dir, name=name, Name=name.capitalize(), version=ver,
        p3d_path=basename(p3d_path), platform='linux_'+platform,
        nointernet=nointernet, icons=ico_str)
    system(cmd)
    move('linux_' + platform + '/' + name, 'img/data/' + name)


def __bld_packages(name, platform, int_str):
    with InsideDir('img'):
        system('zip -9r ../pdata.zip *')
    system('cat pdata.zip >> ./mojosetup_' + platform)
    dst = '%s-%s%s-linux_%s' % (name, branch, int_str, platform)
    move('mojosetup_' + platform, dst)
    system('chmod +x %s-%s%s-linux_%s' % (name, branch, int_str, platform))
    src = '%s-%s%s-linux_%s' % (name, branch, int_str, platform)
    move(src, '../%s-%s%s-linux_%s' % (name, branch, int_str, platform))
