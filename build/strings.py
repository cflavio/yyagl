from os import system, makedirs, remove
from os.path import exists
from shutil import move, copy
from yyagl.build.build import files


def bld_mo(target, source, env):
    lng_dir_code, appname = env['LNG'], env['APPNAME']
    lng_code = str(target)[len(lng_dir_code):].split('/')[0]
    __bld_mo(lng_code, lng_code, env)


def __bld_mo(lng, lng_code, env):
    lng_dir = env['LNG'] + lng + '/LC_MESSAGES/'
    cmd = 'msgfmt -o {lng_dir}{appname}.mo assets/po/{lng_code}.po'
    system(cmd.format(lng_dir=lng_dir, appname=env['APPNAME'], lng_code=lng_code))


def bld_pot(target, source, env):
    src_files = ' '.join(files(['py'], ['feedparser', 'venv', 'thirdparty']))
    lng_dir, appname = env['LNG'], env['APPNAME']
    cmd_tmpl = 'xgettext -ci18n -d {appname} -L python -o assets/po/{appname}.pot '
    system(cmd_tmpl.format(lng_dir=lng_dir, appname=env['APPNAME']) + src_files)


def bld_merge(target, source, env):
    lng_dir, appname = env['LNG'], env['APPNAME']
    lng_code = str(target)[len('assets/po/'):].split('.po')[0]
    __bld_tmpl_merge(lng_dir, lng_code, lng_code, appname)


def __bld_tmpl_merge(lng_dir, lng_code, lng, appname):
    lng_base_dir = __prepare(lng_dir, lng, appname)
    __merge(lng_base_dir, lng_code, appname)
    __postprocess(lng_base_dir, lng_code, appname)


def __prepare(lng_base_dir, lng, appname):
    if not exists(lng_base_dir + lng + '/LC_MESSAGES'):
        makedirs(lng_base_dir + lng + '/LC_MESSAGES')
    lng_dir = lng_base_dir + lng + '/LC_MESSAGES/'
    if not exists('assets/po/' + lng + '.po'):
        lines_to_fix = ['CHARSET/UTF-8', 'ENCODING/8bit']
        list(map(lambda line: __fix_line(line, lng_dir, appname), lines_to_fix))
        copy(lng_dir + appname + '.pot', lng_dir + appname + '.po')
    return lng_dir


def __fix_line(line, lng_dir, appname):
    cmd_tmpl = "sed 's/{line}/' {lng_dir}{appname}.pot > " + \
        "{lng_dir}{appname}tmp.po"
    system(cmd_tmpl.format(line=line, lng_dir=lng_dir, appname=appname))
    move(lng_dir + appname + 'tmp.po', lng_dir + appname + '.pot')


def __merge(lng_dir, lng_code, appname):
    cmd_str = 'msgmerge -o {lng_dir}{appname}merge.po ' + \
        'assets/po/{lng_code}.po assets/po/{appname}.pot'
    system(cmd_str.format(lng_dir=lng_dir, lng_code=lng_code, appname=appname))
    copy(lng_dir + appname + 'merge.po', 'assets/po/%s.po' % lng_code)
    remove('{lng_dir}{appname}merge.po'.format(lng_dir=lng_dir, appname=appname))

def __postprocess(lng_dir, lng_code, appname):
    lines = open('assets/po/%s.po' % lng_code, 'r').readlines()
    with open('assets/po/%s.po' % lng_code, 'w') as outf:
        for line in lines:
            po_str = '"POT-Creation-Date: YEAR-MO-DA HO:MI+ZONE\\n"\n'
            outf.write(po_str if line.startswith(po_str[:20]) else line)
