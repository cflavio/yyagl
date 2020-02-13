from os import system, chdir
from yyagl.build.build import bld_dpath, branch, exec_cmd, test_fpath


def bld_ut(target, source, env):
    # this doesn't work: unittest's outuput in sandboxed
    # with open('tests.txt', 'w') as outf: outf.write(exec_cmd('python -m unittest'))
    #chdir('..')
    system('python -m unittest 2> tests.txt')
    # alternatively i could replace it with TestLoader().loadTests...
    # and TextTestRunner(stream=sys.stdout).run(...)
    cmd = 'tar -czf {out_name} tests.txt && rm tests.txt'
    fpath = test_fpath.format(dst_dir=bld_dpath, appname=env['APPNAME'],
                              version=branch)
    system(cmd.format(out_name=fpath))
