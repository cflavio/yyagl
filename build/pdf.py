from os import system, rename, remove
from itertools import product
from shutil import move
from .build import bld_dpath, branch, pdf_fpath


def build_pdf(target, source, env):
    cmd_tmpl = "enscript --font=Courier10 --continuous-page-numbers " + \
        "--line-numbers {lng} -o - `find {root} {wildcard} {filter}` | " + \
        "ps2pdf - {name}.pdf"
    cmd_cont_tmpl = "tail -n +1 `find {root} {wildcard} {filter}` " + \
        "| sed 's/==> /# ==> /' > temp.txt ; enscript --font=Courier10 " + \
        "--continuous-page-numbers --no-header {lng} -o - temp.txt | " + \
        "ps2pdf - {name}.pdf ; rm temp.txt"
    for name, options in env['PDF_CONF'].items():
        for (i, opt), suff in product(enumerate(options), ['', '_cont']):
            cmd = cmd_cont_tmpl if suff else cmd_tmpl
            __process(opt, cmd, name + suff, i)
        cmd_pdf_tmpl = 'pdfnup --nup 2x1 -o {name}.pdf {name}.pdf'
        for name_s in [name + '', name + '_cont']:
            system(cmd_pdf_tmpl.format(name=name_s))
    __build_pkg(env)


def __process_step(name, cmd):
    rename(name + '.pdf', name + '_append.pdf')
    system(cmd)
    cmd = 'gs -q -sPAPERSIZE=a4 -dNOPAUSE -dBATCH -sDEVICE=pdfwrite ' + \
        '-sOutputFile={name}-joined.pdf {name}_append.pdf {name}.pdf'
    system(cmd.format(name=name))
    map(remove, ['%s%s.pdf' % (name, suff) for suff in ['', '_append']])
    move(name + '-joined.pdf', name + '.pdf')


def __process(opt, cmd_tmpl, name, i):
    filt = ''.join(["-not -path '%s' " % fil for fil in opt[3]])
    lng = ('--pretty-print=' + opt[0]) if opt[0] else ''
    wcard = '-o '.join(["-name '%s' " % wld for wld in opt[2].split()])
    wcard = '\\( %s\\)' % wcard
    cmd = cmd_tmpl.format(lng=lng, root=opt[1], wildcard=wcard, filter=filt,
                          name=name)
    __process_step(name, cmd) if i else system(cmd)


def __build_pkg(env):
    pdfs = ''.join([name + '.pdf ' for name in env['PDF_CONF']])
    pdfs += ''.join([name + '_cont.pdf ' for name in env['PDF_CONF']])
    cmd = 'tar -czf {out_name} ' + pdfs + ' && rm ' + pdfs
    pdf_path = pdf_fpath.format(path=bld_dpath, appname=env['APPNAME'],
                                version=branch)
    system(cmd.format(out_name=pdf_path))
