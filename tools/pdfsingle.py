# python yyagl/tools/pdfsingle.py path/to/file.py
from os import chdir, getcwd, system
from os.path import dirname, basename, exists
from sys import argv


class InsideDir:

    def __init__(self, dir_):
        self.dir = dir_
        self.old_dir = getcwd()

    def __enter__(self):
        chdir(self.dir)

    def __exit__(self, exc_type, exc_val, exc_tb):
        chdir(self.old_dir)


filename = argv[1]
name = basename(filename)
path = dirname(filename)
noext = name.rsplit('.', 1)[0]
test_tmpl = "tail -n +1 {found} " + \
    "| sed 's/==> /# ==> /' > tmp.txt ; enscript --font=Courier10 " + \
    "--continuous-page-numbers --no-header --pretty-print=python " + \
    "-o - tmp.txt | ps2pdf - {name}.pdf ; rm tmp.txt"
found = filename
with InsideDir('yyagl/tests/' + path):
    if exists('test_' + name):
        found += ' yyagl/tests/%s/test_%s' % (path, name)
test_cmd = test_tmpl.format(name=noext, found=found)
system(test_cmd)
system('pdfnup --nup 2x1 -o {noext}.pdf {noext}.pdf'.format(noext=noext))
