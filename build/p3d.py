from os import remove, system, path as os_path, walk
from os.path import dirname, realpath
from shutil import move
from .build import ver, bld_dir


def build_p3d(target, source, env):
    start_dir = os_path.abspath('.') + '/'
    file_path = dirname(realpath(__file__))
    curr_dir = dirname(realpath(file_path))
    yyaglpath = curr_dir[len(start_dir):].replace('/', '\/')
    seds = [('version', ''), ('Name', ''), ('name', ''), ('yyaglpath', 'g')]
    seds = ["-e 's/<%s>/{%s}/%s'" % (sel[0], sel[0], sel[1]) for sel in seds]
    seds = ' '.join(seds)
    sed_tmpl = "sed %s {curr_dir}template.pdef > {name}.pdef" % seds
    sed_cmd = sed_tmpl.format(
        version=ver, Name=env['APPNAME'].capitalize(), name=env['APPNAME'],
        curr_dir=file_path + '/', yyaglpath=yyaglpath)
    system(sed_cmd)
    with open(env['APPNAME'] + '.pdef') as pdef:
        with open(env['APPNAME'] + 'nopygame.pdef', 'w') as pdef_nopygame:
            pdef_nopygame.write(pdef.read().replace(", 'pygame'", ""))
    build('', env)
    build('nopygame', env)


def build(suff, env):
    system('ppackage -i %s %s%s.pdef' % (bld_dir, env['APPNAME'], suff))
    p3d_src_tmpl = '{path}{Name}.{version}.p3d'
    p3d_src = p3d_src_tmpl.format(
        path=bld_dir, Name=env['APPNAME'].capitalize(), version=ver, suff=suff)
    move(p3d_src, env['P3D_PATH'][:-4] + suff + '.p3d')
    remove(env['APPNAME'] + suff + '.pdef')
