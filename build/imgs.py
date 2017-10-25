from os import system, remove
from sys import executable
from build import exec_cmd
from mtprocesser import MultithreadedProcesser


def bld_images(target, source, env):
    mp_mgr = MultithreadedProcesser()
    map(__bld_img, [(str(src), mp_mgr) for src in source])
    output = mp_mgr.run()


def __bld_img(fname_mp_mgr):
    fname, mp_mgr = fname_mp_mgr
    mp_mgr.add(executable + ' ./yyagl/build/img2txo.py "%s"' % fname)
