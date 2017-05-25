from os import system
from os.path import dirname, realpath, abspath
from shutil import rmtree, copytree
from .build import bld_dpath, branch, docs_fpath


def bld_docs(target, source, env):
    __prepare(env)
    system('sphinx-apidoc -o %sdocs_apidoc .' % bld_dpath)
    system('sed -i 1s/./Modules/ %sdocs_apidoc/modules.rst' % bld_dpath)
    system('sphinx-build -b html %sdocs_apidoc %sdocs' % ((bld_dpath,) * 2))
    bld_cmd = 'tar -C {path} -czf {fpath} ./docs'
    fpath = docs_fpath.format(path=bld_dpath, appname=env['APPNAME'],
                              version=branch)
    system(bld_cmd.format(path=bld_dpath, fpath=fpath))
    __clean()


def __prepare(env):
    curr_dir = dirname(realpath(__file__)) + '/'
    copytree(curr_dir + 'docs', bld_dpath + 'docs_apidoc')
    cmd = 'sed -i.bak -e "s/<appname>/%s/" %sdocs_apidoc/index.rst'
    system(cmd % (env['APPNAME'].capitalize(), bld_dpath))
    curr_dir = abspath('.').replace('/', '\/')
    curr_dir = curr_dir.replace('\\', '\\\\')
    args = ['appname', 'src_dir', 'version']
    args = ['-e "s/<%s>/{%s}/"' % ((arg,) * 2) for arg in args]
    cmd_tmpl = 'sed -i.bak %s {dir}docs_apidoc/conf.py' % ' '.join(args)
    cmd = cmd_tmpl.format(
        appname=env['APPNAME'].capitalize(), version=branch, dir=bld_dpath,
        src_dir=curr_dir)
    system(cmd)


def __clean():
    map(rmtree, [bld_dpath + dir for dir in ['docs_apidoc', 'docs']])
