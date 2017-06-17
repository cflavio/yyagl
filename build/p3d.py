from os import remove, system, path as os_path
from os.path import dirname, realpath
from shutil import move
from .build import ver, bld_dpath


def bld_p3d(target, source, env):
    start_dir = os_path.abspath('.') + '/'
    fpath = dirname(realpath(__file__))
    curr_dir = dirname(realpath(fpath))
    yyaglpath = curr_dir[len(start_dir):].replace('/', '\/')
    seds = [('version', ''), ('AppName', ''), ('appname', ''),
            ('yyaglpath', 'g')]
    seds = ["-e 's/<%s>/{%s}/%s'" % (sel[0], sel[0], sel[1]) for sel in seds]
    tmpl = 'sed %s {curr_dir}template.pdef > {appname}.pdef' % ' '.join(seds)
    cmd = tmpl.format(
        version=ver, AppName=env['APPNAME'].capitalize(),
        appname=env['APPNAME'], curr_dir=fpath + '/', yyaglpath=yyaglpath)
    system(cmd)
    with open(env['APPNAME'] + '.pdef') as fpdef:
        with open(env['APPNAME'] + 'nopygame.pdef', 'w') as fpdef_nopygame:
            fpdef_nopygame.write(fpdef.read().replace(", 'pygame'", ""))
    map(lambda suff: __bld(suff, env), ['', 'nopygame'])


def __bld(suff, env):
    system('ppackage -i %s %s%s.pdef' % (bld_dpath, env['APPNAME'], suff))
    p3d_src_tmpl = '{src_dir}{AppName}.{version}.p3d'
    p3d_src = p3d_src_tmpl.format(
        src_dir=bld_dpath, AppName=env['APPNAME'].capitalize(), version=ver,
        suff=suff)
    move(p3d_src, env['P3D_PATH'][:-4] + suff + '.p3d')
    remove(env['APPNAME'] + suff + '.pdef')
