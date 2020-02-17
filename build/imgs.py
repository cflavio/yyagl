from os import system, remove
from os.path import dirname
from sys import executable
from yyagl.build.mtprocesser import MultithreadedProcesser


def bld_images(target, source, env):
    mp_mgr = MultithreadedProcesser(env['CORES'])
    list(map(__bld_img, [(str(src), mp_mgr) for src in source]))
    mp_mgr.run()


def __bld_img(fname_mp_mgr):
    fname, mp_mgr = fname_mp_mgr
    curr_path = dirname(__file__)
    mp_mgr.add(executable + ' %s/img2txo.py "%s"' % (curr_path, fname))
