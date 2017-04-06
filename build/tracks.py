from os import remove, system, path as os_path, walk
from os.path import dirname, realpath
from shutil import move
from .build import ver, path


def build_tracks(target, source, env):
    for root, dirnames, filenames in walk('assets/models'):
        for filename in filenames:
            fname = root + '/' + filename
            if fname.endswith('.egg'):
                system('egg2bam %s -o %s' %(fname, fname[:-3] + 'bam'))
    for root, dirnames, filenames in walk('assets/models/tracks'):
        for dname in dirnames:
            if root == 'assets/models/tracks':
                system('python yyagl/build/process_track.py ' + dname)
