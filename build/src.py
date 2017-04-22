from os import system
from .build import src_file, branch, bld_dir


def build_src(target, source, env):
    excl = [
        '{pkg_name}', 'built', '.git', '.kdev4', '{name}.kdev4',
        '.sconsign.dblite', '*.pyc', '.settings', '.project', '.pydevproject',
        '{name}.geany']
    excl = ' '.join(["--exclude '%s'" % exc for exc in excl])
    bld_cmd = "tar --transform 's/^./{name}/' -czf {pkg_name} %s ." % excl
    pkg_name = src_file.format(path=bld_dir, name=env['APPNAME'],
                               version=branch)
    system(bld_cmd.format(name=env['APPNAME'], pkg_name=pkg_name))
