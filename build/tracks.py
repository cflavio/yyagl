from os import system, walk
from sys import executable
from .mtprocesser import MultithreadedProcesser


def bld_models(target, source, env):
    mp_mgr = MultithreadedProcesser()
    for root, dnames, fnames in walk(env['MODELS_DIR_PATH']):
        if not root.startswith(env['TRACKS_DIR_PATH']):
            for fname in [fname for fname in fnames if fname.endswith('.egg')]:
                __process_model(root, fname, mp_mgr)
    mp_mgr.run()
    for root, dnames, fnames in walk('assets/models/tracks'):
        for dname in dnames:
            if root == env['TRACKS_DIR_PATH']: __process_track(dname)


def __process_model(root, fname, mp_mgr):
    _fname = root + '/' + fname
    cmd_args = _fname, _fname[:-3] + 'bam'
    mp_mgr.add('egg2bam -txo -mipmap -ctex %s -o %s' % cmd_args)


def __process_track(dname):
    system(executable + ' yyagl/build/process_track.py ' + dname)
