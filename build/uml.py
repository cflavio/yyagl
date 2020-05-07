from os import system, walk, remove, makedirs, listdir, getcwd
from os.path import exists, isfile, join, basename
from shutil import move, rmtree
from yyagl.build.build import exec_cmd


def bld_uml(target, source, env):  # unused target, source
    if exists('assets/uml'):
        if exists('assets/uml/class_diagram.txt'):
            system('plantuml assets/uml/class_diagram.txt')
        if exists('assets/uml/sequence_diagrams.txt'):
            system('plantuml assets/uml/sequence_diagrams.txt')
            system('convert assets/uml/sequence_diagrams*.png '
                   'assets/uml/sequence_diagrams.pdf')
            system('rm assets/uml/sequence_diagrams*.png')
            system('pdfnup --nup 3x2 -o assets/uml/sequence_diagrams.pdf '
                   'assets/uml/sequence_diagrams.pdf')
    auto_classes(env)


def auto_classes(env):
    if exists('built/tmp_uml'): rmtree('built/tmp_uml')
    if exists('built/uml_classes'): rmtree('built/uml_classes')
    if exists('built/uml_classes.zip'): remove('built/uml_classes.zip')
    for root, _, filenames in walk('.'):
        if not exists('built/tmp_uml'): makedirs('built/tmp_uml')
        for filename in filenames:
            if not root.startswith('./wvenv/') and \
                    not root.startswith('./venv/')and \
                    not root.startswith('./thirdparty/') and \
                    filename.endswith('.py') and \
                    not filename.endswith('__init__.py') and \
                    not any(root == './' + filtered or
                            root.startswith('./%s/' % filtered)
                            for filtered in env['UML_FILTER']):
                _root = root[2:]
                path = _root + ('/' if _root else '') + filename
                name = path[:-3].replace('/', '_')
                system('pyreverse -o png -p %s %s -fALL -m y' % (name, path))
                fname = 'classes_' + name + '.png'
                if exists(fname): move(fname, 'built/tmp_uml/' + fname)
        pkgname = root.lstrip('./').replace('/', '_')
        if not pkgname: pkgname = basename(getcwd())
        buildpkg(pkgname)
    pdfs = [f for f in listdir('built/uml_classes')
            if isfile(join('built/uml_classes', f))]
    pdfs = [f for f in pdfs if f.endswith('.pdf') and f != '.pdf']
    pdfs = ['built/uml_classes/' + f for f in pdfs]
    system('echo "" | ps2pdf -sPAPERSIZE=a4 - built/uml_classes/blank.pdf')
    for pdf in pdfs:
        numpages = exec_cmd(
            b'pdftk %s dump_data | grep NumberOfPages' % bytes(pdf, 'utf-8'))
        numpages = int(numpages.lstrip('NumberOfPages: '))
        # suspicious argument in lstrip
        if numpages % 2:
            system('pdftk %s built/uml_classes/blank.pdf cat output %s2 && mv '
                   '%s2 %s' % (pdf, pdf, pdf, pdf))
    remove('built/uml_classes/blank.pdf')
    system('pdftk built/uml_classes/*.pdf cat output '
           'built/uml_classes/all.pdf')
    system('zip -r built/uml_classes.zip built/uml_classes')
    rmtree('built/uml_classes')
    rmtree('built/tmp_uml')


def nextfile(finfo, posx, posy, width, height):
    fnames = [finfo_[0] for finfo_ in finfo]
    finfo = get_finfo(fnames, width, height)
    for info in finfo:
        if info[1][0] + posx <= width and info[1][1] + posy <= height:
            finfo.remove(info)
            return info, finfo
    for info in finfo:
        if info[1][1] + posy <= height:
            finfo.remove(info)
            return info, finfo
    info = finfo.pop(0)
    return info, finfo


def get_finfo(fnames, width, height):
    _finfo = []
    for fname in fnames:
        fname = fname
        geometry = exec_cmd('identify -verbose "%s" | grep Geometry' % fname)
        split_dim = lambda geom: geom.split()[1].split('+')[0].split('x')
        size = [int(dim) for dim in split_dim(geometry)]
        if size[0] > width or size[1] > height:
            cmd = 'convert %s -resize %sx%s\> %s' % (
                fname, width, height, fname)
            # anomalous backslash in string
            exec_cmd(cmd)
        geometry = exec_cmd('identify -verbose "%s" | grep Geometry' % fname)
        split_dim = lambda geom: geom.split()[1].split('+')[0].split('x')
        size = [int(dim) for dim in split_dim(geometry)]
        _finfo += [(fname, size)]
    # finfo = list(sorted(finfo, key=lambda elm: elm[1][0]))
    # finfo = list(reversed(sorted(finfo, key=lambda elm: elm[1][1])))
    _finfo = list(reversed(
        sorted(_finfo, key=lambda elm: elm[1][0] * elm[1][1])))
    return _finfo


def buildpkg(pkgname):
    fnames = [f for f in listdir('built/tmp_uml')
              if isfile(join('built/tmp_uml', f))]
    fnames = ['built/tmp_uml/' + f for f in fnames]
    if not fnames: return
    finfo = []
    width = 1200
    height = int(round(width * 297.0 / 210.0))
    finfo = get_finfo(fnames, width, height)
    page = 0
    posx = posy = lineh = 0

    def newpage(page):
        page += 1
        cmd = 'convert -size %sx%s xc:white built/tmp_uml/page%s.png' % (
            width, height, page)
        exec_cmd(cmd)
        return page, 0, 0, 0
    page, posx, posy, lineh = newpage(page)
    margin = 40
    while finfo:
        info, finfo = nextfile(
            finfo, posx, posy + lineh + margin, width, height)
        new_img = info[0]
        dst_img = 'built/tmp_uml/page%s.png' % page
        if posx + info[1][0] <= width and posy + info[1][1] <= height:
            cmd = 'composite -geometry +%s+%s -gravity NorthWest %s %s %s' % (
                posx, posy, new_img, dst_img, dst_img)
            exec_cmd(cmd)
            posx += info[1][0] + margin
            if info[1][1] > lineh: lineh = info[1][1]
        else:
            posx = 0
            posy += lineh + margin
            if posy + info[1][1] <= height:
                cmd = 'composite -geometry +%s+%s -gravity NorthWest %s %s %s' \
                    % (posx, posy, new_img, dst_img, dst_img)
                exec_cmd(cmd)
                posx = info[1][0] + margin
                lineh = info[1][1]
            else:
                page, posx, posy, lineh = newpage(page)
                dst_img = 'built/tmp_uml/page%s.png' % page
                cmd = 'composite -geometry +%s+%s -gravity NorthWest %s %s %s' \
                    % (posx, posy, new_img, dst_img, dst_img)
                exec_cmd(cmd)
                posx = info[1][0] + margin
                lineh = info[1][1]

    # system('convert -page a5 -rotate 90 -background white '
    #        'built/tmp_uml/classes_*.png built/tmp_uml/uml_classes.pdf')
    # system('pdfnup --nup 3x2 -o built/uml_classes.pdf '
    #        'built/tmp_uml/uml_classes.pdf')
    if not exists('built/uml_classes'): makedirs('built/uml_classes')
    outname = 'built/uml_classes/%s.pdf' % pkgname
    system('convert built/tmp_uml/page*.png %s' % outname)
    system('pdfcrop --margin "32 32 32 32" %s %s' % (outname, outname))
    rmtree('built/tmp_uml')
