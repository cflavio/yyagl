from os import system
from .build import bld_dpath, branch, exec_cmd, test_fpath


def bld_ut(target, source, env):
    with open('tests.txt', 'w') as outf: outf.write(exec_cmd('nosetests'))
    cmd = 'tar -czf {out_name} tests.txt && rm tests.txt'
    fpath = test_fpath.format(dst_dir=bld_dpath, appname=env['APPNAME'],
                              version=branch)
    system(cmd.format(out_name=fpath))
