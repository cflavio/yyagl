from os import remove, system, path as os_path
from os.path import dirname, realpath
from shutil import move
from .build import ver, path


def build(suff, env):
    if env['SUPERMIRROR']:
        cmd_template = 'panda3d -M {ptools_path} ' + \
            '{ptools_path}/ppackage1.9.p3d -S ' + \
            '{ptools_path}/mycert.pem -i {path} {name}{suff}.pdef'
        cmd_str = cmd_template.format(
            ptools_path=env['SUPERMIRROR'], path=path, name=env['NAME'],
            suff=suff)
    else:
        cmd_str = 'ppackage -i %s %s%s.pdef' % (path, env['NAME'], suff)
    system(cmd_str)
    p3d_src_tmpl = '{path}{Name}.{version}.p3d'
    p3d_src = p3d_src_tmpl.format(path=path, Name=env['NAME'].capitalize(),
                                  version=ver, suff=suff)
    move(p3d_src, env['P3D_PATH'][:-4] + suff + '.p3d')
    remove(env['NAME']+suff+'.pdef')


def build_p3d(target, source, env):
    start_dir = os_path.abspath('.') + '/'
    file_path = dirname(realpath(__file__))
    curr_path = dirname(realpath(file_path))
    eng_path = curr_path[len(start_dir):].replace('/', '\/')
    sed_tmpl = "sed -e 's/<version>/{version}/' -e 's/<Name>/{Name}/' " + \
        "-e 's/<name>/{name}/' -e 's/<enginepath>/{eng_path}/g' " + \
        "{curr_path}template.pdef > {name}.pdef"
    sed_cmd = sed_tmpl.format(
        version=ver, Name=env['NAME'].capitalize(), name=env['NAME'],
        curr_path=file_path + '/', eng_path=eng_path)
    system(sed_cmd)
    with open(env['NAME'] + '.pdef') as pdef:
        with open(env['NAME'] + 'nopygame.pdef', 'w') as pdef_nopygame:
            pdef_nopygame.write(pdef.read().replace(", 'pygame'", ""))
    build('', env)
    build('nopygame', env)
