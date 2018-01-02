from os import system, walk
from .mtprocesser import MultithreadedProcesser


def bld_models(target, source, env):
    system('pip install psutil')
    mp_mgr = MultithreadedProcesser(env['CORES'])
    for root, dnames, fnames in walk(env['MODELS_DIR_PATH']):
        if not root.startswith(env['TRACKS_DIR_PATH']):
            for fname in [fname for fname in fnames if fname.endswith('.egg')]:
                __process_model(root, fname, mp_mgr)
    mp_mgr.run()
    for root, dnames, fnames in walk('assets/models/tracks'):
        for dname in dnames:
            if root == env['TRACKS_DIR_PATH']: __process_track(dname, env['CORES'])


def __process_model(root, fname, mp_mgr):
    _fname = root + '/' + fname
    cmd_args = _fname, _fname[:-3] + 'bam'
    mp_mgr.add('egg2bam -txo -mipmap -ctex %s -o %s' % cmd_args)


def __process_track(dname, cores):
    system('python yyagl/build/process_track.py %s %s' % (dname, cores))
    # we don't use sys.executable in place of python since we need to
    # dynamically detect the "current" python i.e. otherwise it would pick
    # the "wrong" python in buildbot and use an old panda version, and it
    # fails with models built with the new egg2bam
