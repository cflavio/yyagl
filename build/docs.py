from os import system
from os.path import dirname, realpath, abspath
from shutil import rmtree, copytree
from .build import bld_dir, branch, docs_file


def build_docs(target, source, env):
    __prepare(env)
    system('sphinx-apidoc -o %sdocs_apidoc .' % bld_dir)
    system("sed -i 1s/./Modules/ %sdocs_apidoc/modules.rst" % bld_dir)
    system('sphinx-build -b html %sdocs_apidoc %sdocs' % (bld_dir, bld_dir))
    bld_cmd = 'tar -C {path} -czf {out_name} ./docs'
    f_out = docs_file.format(path=bld_dir, name=env['APPNAME'],
                             version=branch)
    system(bld_cmd.format(path=bld_dir, out_name=f_out))
    __clean()


def __prepare(env):
    curr_dir = dirname(realpath(__file__)) + '/'
    copytree(curr_dir + 'docs', bld_dir + 'docs_apidoc')
    cmd = 'sed -i.bak -e "s/<appname>/%s/" %sdocs_apidoc/index.rst'
    system(cmd % (env['APPNAME'].capitalize(), bld_dir))
    curr_dir = abspath('.').replace('/', '\/')
    curr_dir = curr_dir.replace('\\', '\\\\')
    args = ['appname', 'src_path', 'version']
    args = ['-e "s/<%s>/{%s}/"' % (arg, arg) for arg in args ]
    cmd_tmpl = 'sed -i.bak ' + (' '.join(args)) + ' {path}docs_apidoc/conf.py'
    cmd = cmd_tmpl.format(
        appname=env['APPNAME'].capitalize(), version=branch, path=bld_dir,
        src_path=curr_dir)
    system(cmd)


def __clean():
    map(rmtree, [bld_dir + 'docs_apidoc', bld_dir + 'docs'])
