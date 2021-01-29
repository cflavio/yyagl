from os import system, rename, remove, mkdir
from os.path import exists, dirname, basename
from itertools import product
from shutil import move
from yyagl.build.build import bld_dpath, branch, pdf_fpath, exec_cmd


def bld_pdfs(target, source, env):  # unused target, source
    pdfconf = env['PDF_CONF'].items()
    if not exists('built'): mkdir('built')
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
    test_tmpl = "tail -n +1 {found} " + \
        "| sed 's/==> /# ==> /' > tmp.txt ; enscript --font=Courier10 " + \
        "--continuous-page-numbers --no-header {lng} -o - tmp.txt | " + \
        "ps2pdf - {name}.pdf ; rm tmp.txt"
    # command for generating a pdf with appended files
    for (i, opt), suff in product(enumerate(opts), ['', '_cont', '_test']):
        if suff == '': curr_tmpl = tmpl
        elif suff == '_cont': curr_tmpl = cont_tmpl
        else: curr_tmpl = test_tmpl
        __process(opt, curr_tmpl, name + suff, i)
    pdf_tmpl = 'pdfnup --nup 2x1 -o {name}.pdf {name}.pdf'
    suffixes = [name + '', name + '_cont', name + '_test']
    list(map(
        lambda name_suff: system(pdf_tmpl.format(name=name_suff)), suffixes))


def __process(opt, tmpl, name, i):
    filt = ''.join(["-not -path '%s' " % fil for fil in opt.excl])
    lng = ('--pretty-print=' + opt.lng) if opt.lng else ''
    wcard = '-o '.join(["-name '%s' " % wld for wld in opt.fil.split()])
    wcard = '\\( %s\\)' % wcard
    found = __myfind(opt.root, wcard, filt)
    cmd = tmpl.format(lng=lng, root=opt.root, wildcard=wcard, filter=filt,
                      name=name, found=found)
    __process_step(name, cmd) if i else system(cmd)


def __myfind(root, wildcard, _filter):
    tmpl = 'find {root} {wildcard} {filter}'
    cmd = tmpl.format(root=root, wildcard=wildcard, filter=_filter)
    found_files = exec_cmd(cmd)
    found_files = found_files.split('\n')
    ret = []
    for _file in found_files:
        ret += [_file]
        dirn = dirname(_file)
        basen = basename(_file)
        if not _file.startswith('./yyagl'): continue
        testn = './yyagl/tests/' + dirn[2:] + '/test_' + basen
        if exists(testn): ret += [testn]
    return ' '.join(ret)


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
    pdfs += ''.join([name + '_test.pdf ' for name in env['PDF_CONF']])
    cmd = 'tar -czf {fout} ' + pdfs + ' && rm ' + pdfs
    pdf_path = pdf_fpath.format(dst_dir=bld_dpath, appname=env['APPNAME'],
                                version=branch)
    system(cmd.format(fout=pdf_path))
