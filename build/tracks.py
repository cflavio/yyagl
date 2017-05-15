from os import system, walk


def build_tracks(target, source, env):
    for root, dirnames, filenames in walk('assets/models'):
        for filename in filenames:
            fname = root + '/' + filename
            if fname.endswith('.egg'):
                system('egg2bam -txo -mipmap -ctex %s -o %s' % (fname, fname[:-3] + 'bam'))
    for root, dirnames, filenames in walk('assets/models/tracks'):
        for dname in dirnames:
            if root == 'assets/models/tracks':
                system('python yyagl/build/process_track.py ' + dname)
