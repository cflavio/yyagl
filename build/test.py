from os import system
from .build import bld_dir, branch, exec_cmd, test_file


def build_ut(target, source, env):
    with open('tests.txt', 'w') as outfile:
        outfile.write(exec_cmd('nosetests'))
    bld_cmd = 'tar -czf {out_name} tests.txt && rm tests.txt'
    fpath = test_file.format(path=bld_dir, name=env['APPNAME'], version=branch)
    system(bld_cmd.format(out_name=fpath))
