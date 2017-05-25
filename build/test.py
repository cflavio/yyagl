from os import system
from .build import bld_dpath, branch, exec_cmd, test_fpath


def build_ut(target, source, env):
    with open('tests.txt', 'w') as outfile:
        outfile.write(exec_cmd('nosetests'))
    bld_cmd = 'tar -czf {out_name} tests.txt && rm tests.txt'
    fpath = test_fpath.format(path=bld_dpath, name=env['APPNAME'], version=branch)
    system(bld_cmd.format(out_name=fpath))
