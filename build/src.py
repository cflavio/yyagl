from os import system
from .build import src_fpath, branch, bld_dpath


def bld_src(target, source, env):
    excl = [
        '{pkg_name}', 'built', '.git', '.kdev4', '{appname}.kdev4',
        '.sconsign.dblite', '*.pyc', '.settings', '.project', '.pydevproject',
        '{appname}.geany']
    excl = ' '.join(["--exclude '%s'" % exc for exc in excl])
    cmd = "tar --transform 's/^./{appname}/' -czf {pkg_name} %s ." % excl
    pkg_name = src_fpath.format(path=bld_dpath, appname=env['APPNAME'],
                                version=branch)
    system(cmd.format(appname=env['APPNAME'], pkg_name=pkg_name))
