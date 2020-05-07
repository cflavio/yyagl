from os import system
from yyagl.build.build import src_fpath, branch, bld_dpath


def bld_src(target, source, env):  # unused target, source
    fexcl = [
        '{pkg_name}', 'built', '.git', '.kdev4', '{appname}.kdev4',
        '.sconsign.dblite', '*.pyc', '.settings', '.project', '.pydevproject',
        '{appname}.geany']
    excl = ' '.join(["--exclude '%s'" % exc for exc in fexcl])
    cmd = "tar --transform 's/^./{appname}/' -cvzf {pkg_name} %s ." % excl
    pkg_name = src_fpath.format(dst_dir=bld_dpath, appname=env['APPNAME'],
                                version=branch)
    system(cmd.format(appname=env['APPNAME'], pkg_name=pkg_name))
