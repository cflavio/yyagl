from os import system, rename, remove
from itertools import product
from shutil import move
from .build import bld_dpath, branch, pdf_fpath


def bld_pdf(target, source, env):
    tmpl = "enscript --font=Courier10 --continuous-page-numbers " + \
        "--line-numbers {lng} -o - `find {root} {wildcard} {filter}` | " + \
        "ps2pdf - {name}.pdf"
    cont_tmpl = "tail -n +1 `find {root} {wildcard} {filter}` " + \
        "| sed 's/==> /# ==> /' > tmp.txt ; enscript --font=Courier10 " + \
        "--continuous-page-numbers --no-header {lng} -o - tmp.txt | " + \
        "ps2pdf - {name}.pdf ; rm tmp.txt"
    for name, opts in env['PDF_CONF'].items():
        for (i, opt), suff in product(enumerate(opts), ['', '_cont']):
            cmd = cont_tmpl if suff else tmpl
            __process(opt, cmd, name + suff, i)
        pdf_tmpl = 'pdfnup --nup 2x1 -o {name}.pdf {name}.pdf'
        for name_suff in [name + '', name + '_cont']:
            system(pdf_tmpl.format(name=name_suff))
    __bld_pkg(env)


def __process(opt, tmpl, name, i):
    filt = ''.join(["-not -path '%s' " % fil for fil in opt[3]])
    lng = ('--pretty-print=' + opt[0]) if opt[0] else ''
    wcard = '-o '.join(["-name '%s' " % wld for wld in opt[2].split()])
    wcard = '\\( %s\\)' % wcard
    cmd = tmpl.format(lng=lng, root=opt[1], wildcard=wcard, filter=filt,
                      name=name)
    __process_step(name, cmd) if i else system(cmd)


def __process_step(name, cmd):
    rename(name + '.pdf', name + '_append.pdf')
    system(cmd)
    cmd = 'gs -q -sPAPERSIZE=a4 -dNOPAUSE -dBATCH -sDEVICE=pdfwrite ' + \
        '-sOutputFile={name}-joined.pdf {name}_append.pdf {name}.pdf'
    system(cmd.format(name=name))
    map(remove, ['%s%s.pdf' % (name, suff) for suff in ['', '_append']])
    move(name + '-joined.pdf', name + '.pdf')


def __bld_pkg(env):
    pdfs = ''.join([name + '.pdf ' for name in env['PDF_CONF']])
    pdfs += ''.join([name + '_cont.pdf ' for name in env['PDF_CONF']])
    cmd = 'tar -czf {fout} ' + pdfs + ' && rm ' + pdfs
    pdf_path = pdf_fpath.format(dst_dir=bld_dpath, appname=env['APPNAME'],
                                version=branch)
    system(cmd.format(fout=pdf_path))
