from os import system, walk
from sys import executable


def bld_tracks(target, source, env):
    for root, dnames, fnames in walk(env['MODELS_DIR']):
        if not root.startswith('assets/models/tracks'):
            for fname in fnames:
                _fname = root + '/' + fname
                if _fname.endswith('.egg'):
                    cmd_args = (_fname, _fname[:-3] + 'bam')
                    system('egg2bam -txo -mipmap -ctex %s -o %s' % cmd_args)
    for root, dnames, fnames in walk('assets/models/tracks'):
        for dname in dnames:
            if root == env['TRACKS_DIR']:
                system(executable + ' yyagl/build/process_track.py ' + dname)
