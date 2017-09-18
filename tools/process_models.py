# usage: python yyagl/tools/process_models.py
from os import system, walk
from sys import executable


for root, _, fnames in walk('assets/models'):
    for fname in [fname for fname in fnames if fname.endswith('.egg')]:
        _fname = root + '/' + fname
        system('egg-trans -nv 30 -o %s %s' % (_fname, _fname))
        system(executable + ' yyagl/tools/apply_gloss.py ' + _fname)
