from os import system, rename, remove
from itertools import product
from shutil import move
from .build import bld_dpath, branch, pdf_fpath


def bld_pdfs(target, source, env):
    pdfconf = env['PDF_CONF'].items()
    list(map(lambda name_opts: __bld_pdf(*name_opts), pdfconf))
    __bld_pkg(env)


def __bld_pdf(name, opts):
    tmpl = "enscript --font=Courier10 --continuous-page-numbers " + \
        "--line-numbers {lng} -o - `find {root} {wildcard} {filter}` | " + \
        "ps2pdf - {name}.pdf"
    # command for generating a pdf with separated files
    cont_tmpl = "tail -n +1 `find {root} {wildcard} {filter}` " + \
        "| sed 's/==> /# ==> /' > tmp.txt ; enscript --font=Courier10 " + \
        "--continuous-page-numbers --no-header {lng} -o - tmp.txt | " + \
        "ps2pdf - {name}.pdf ; rm tmp.txt"
    # command for generating a pdf with appended files
    for (i, opt), suff in product(enumerate(opts), ['', '_cont']):
        __process(opt, cont_tmpl if suff else tmpl, name + suff, i)
    pdf_tmpl = 'pdfnup --nup 2x1 -o {name}.pdf {name}.pdf'
    suffixes = [name + '', name + '_cont']
    list(map(lambda name_suff: system(pdf_tmpl.format(name=name_suff)), suffixes))


def __process(opt, tmpl, name, i):
    filt = ''.join(["-not -path '%s' " % fil for fil in opt.excl])
    lng = ('--pretty-print=' + opt.lng) if opt.lng else ''
    wcard = '-o '.join(["-name '%s' " % wld for wld in opt.fil.split()])
    wcard = '\\( %s\\)' % wcard
    cmd = tmpl.format(lng=lng, root=opt.root, wildcard=wcard, filter=filt,
                      name=name)
    __process_step(name, cmd) if i else system(cmd)


def __process_step(name, cmd):
    rename(name + '.pdf', name + '_append.pdf')
    system(cmd)
    cmd = 'gs -q -sPAPERSIZE=a4 -dNOPAUSE -dBATCH -sDEVICE=pdfwrite ' + \
        '-sOutputFile={name}-joined.pdf {name}_append.pdf {name}.pdf'
    system(cmd.format(name=name))  # concat the pdf
    list(map(remove, ['%s%s.pdf' % (name, suff) for suff in ['', '_append']]))
    move(name + '-joined.pdf', name + '.pdf')


def __bld_pkg(env):
    pdfs = ''.join([name + '.pdf ' for name in env['PDF_CONF']])
    pdfs += ''.join([name + '_cont.pdf ' for name in env['PDF_CONF']])
    cmd = 'tar -czf {fout} ' + pdfs + ' && rm ' + pdfs
    pdf_path = pdf_fpath.format(dst_dir=bld_dpath, appname=env['APPNAME'],
                                version=branch)
    system(cmd.format(fout=pdf_path))
