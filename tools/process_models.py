# usage: python yyagl/tools/process_models.py
from os import system, walk
from sys import executable


for root, dirnames, filenames in walk('assets/models'):
    for filename in filenames:
        fname = root + '/' + filename
        if fname.endswith('.egg'):
            system('egg-trans -nv 30 -o %s %s' % (fname, fname))
            system(executable + ' yyagl/tools/apply_gloss.py ' + fname)
