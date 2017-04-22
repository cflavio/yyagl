from os import system, makedirs
from os.path import exists
from shutil import move, copy
from .build import get_files


def build_strings(target, source, env):
    for lang in env['LANGUAGES']:
        lang_dir = env['LANG'] + lang + '/LC_MESSAGES/'
        cmd = 'msgfmt -o {lang_dir}{name}.mo {lang_dir}{name}.po'
        system(cmd.format(lang_dir=lang_dir, name=env['APPNAME']))


def build_templ_merge(target, source, env):
    src_files = ' '.join(get_files(['py'], ['feedparser', 'venv']))
    cmd_tmpl = 'xgettext -d {appname} -L python -o {appname}.pot '
    system(cmd_tmpl.format(appname=env['APPNAME']) + src_files)
    for lang in env['LANGUAGES']:
        __build_templ_merge(env['LANG'], lang, env['APPNAME'])


def __build_templ_merge(lang_dir, lang, appname):
    path = __prepare(lang_dir, lang, appname)
    __merge(path, appname)
    __postprocess(path, appname)


def __prepare(lang_dir, lang, appname):
    if not exists(lang_dir + lang + '/LC_MESSAGES'):
        makedirs(lang_dir + lang + '/LC_MESSAGES')
    move(appname + '.pot', lang_dir + lang + '/LC_MESSAGES/%s.pot' % appname)
    path = lang_dir + lang + '/LC_MESSAGES/'
    for line in ['CHARSET/UTF-8', 'ENCODING/8bit']:
        cmd_tmpl = "sed 's/{src}/' {lang_dir}{appname}.pot > " + \
            "{lang_dir}{appname}tmp.po"
        system(cmd_tmpl.format(src=line, lang_dir=path, appname=appname))
        move(path + appname + 'tmp.po', path + appname + '.pot')
    if not exists(path + appname + '.po'):
        copy(path + appname + '.pot', path + appname + '.po')
    return path


def __merge(lang_dir, appname):
    cmd_str = 'msgmerge -o {path}{name}merge.po {path}{name}.po ' + \
        '{path}{name}.pot'
    system(cmd_str.format(path=lang_dir, name=appname))
    copy(lang_dir + appname + 'merge.po', lang_dir + appname + '.po')


def __postprocess(lang_dir, appname):
    lines = open(lang_dir + appname + '.po', 'r').readlines()
    with open(lang_dir + appname + '.po', 'w') as outf:
        for line in lines:
            po_str = '"POT-Creation-Date: YEAR-MO-DA HO:MI+ZONE\\n"\n'
            outf.write(po_str if line.startswith(po_str[:20]) else line)
