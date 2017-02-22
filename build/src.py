from os import system
from .build import src_path_str, ver_branch, path


def build_src(target, source, env):
    build_command_str = \
        "tar --transform 's/^./{name}/' -czf {out_name} " + \
        "--exclude '{out_name}' --exclude 'built' --exclude '.git' " + \
        "--exclude '.kdev4' " + \
        "--exclude '{name}.kdev4' --exclude '.sconsign.dblite' " + \
        "--exclude '*.pyc' --exclude .settings --exclude .project " + \
        "--exclude .pydevproject --exclude '{name}.geany' ."
    out_name = src_path_str.format(path=path, name=env['NAME'],
                                   version=ver_branch)
    build_command = build_command_str.format(name=env['NAME'],
                                             out_name=out_name)
    system(build_command)
