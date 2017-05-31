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
    fpath = docs_fpath.format(dst_dir=bld_dpath, appname=env['APPNAME'],
                              version=branch)
    system(bld_cmd.format(path=bld_dpath, fpath=fpath))
    __clean()


def __prepare(env):
    curr_dir = dirname(realpath(__file__)) + '/'
    copytree(curr_dir + 'docs', bld_dpath + 'docs_apidoc')

    args = ['appname', 'DevName', 'devsite', 'prjsite']
    args = ['-e "s/<%s>/{%s}/"' % ((arg,) * 2) for arg in args]
    cmd_tmpl = 'sed -i.bak %s {dst_path}docs_apidoc/index.rst' % ' '.join(args)
    cmd = cmd_tmpl.format(
        appname=env['APPNAME'].capitalize(), DevName='Ya2',
        devsite='http://www.ya2.it', prjsite='http://www.ya2.it/yorg',
        dst_path=bld_dpath)
    system(cmd)
    curr_dir = abspath('.').replace('/', '\/')
    curr_dir = curr_dir.replace('\\', '\\\\')
    args = ['appname', 'src_dpath', 'version', 'DevName', 'htmltheme']
    args = ['-e "s/<%s>/{%s}/"' % ((arg,) * 2) for arg in args]
    cmd_tmpl = 'sed -i.bak %s {dir}docs_apidoc/conf.py' % ' '.join(args)
    cmd = cmd_tmpl.format(
        appname=env['APPNAME'].capitalize(), version=branch, dir=bld_dpath,
        src_dpath=curr_dir, DevName='Ya2', htmltheme='ya2')
    system(cmd)


def __clean():
    map(rmtree, [bld_dpath + dir for dir in ['docs_apidoc', 'docs']])
