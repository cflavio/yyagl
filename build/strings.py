from os import system, makedirs
from os.path import exists
from shutil import move, copy
from .build import get_files


def __build_language(lang_path, lang, name):
    if not exists(lang_path + lang + '/LC_MESSAGES'):
        makedirs(lang_path + lang + '/LC_MESSAGES')
    move(name + '.pot', lang_path + lang + '/LC_MESSAGES/%s.pot' % name)
    path = lang_path + lang + '/LC_MESSAGES/'
    for line in ['CHARSET/UTF-8', 'ENCODING/8bit']:
        cmd_tmpl = "sed 's/{src}/' {path}{name}.pot > {path}{name}tmp.po"
        system(cmd_tmpl.format(src=line, path=path, name=name))
        move(path + name + 'tmp.po', path + name + '.pot')
    if not exists(path + name + '.po'):
        copy(path + name + '.pot', path + name + '.po')
    cmd_str = 'msgmerge -o {path}{name}merge.po {path}{name}.po ' + \
        '{path}{name}.pot'
    system(cmd_str.format(path=path, name=name))
    copy(path + name + 'merge.po', path + name + '.po')
    lines = open(path + name + '.po', 'r').readlines()
    with open(path + name + '.po', 'w') as outf:
        for line in lines:
            po_str = '"POT-Creation-Date: YEAR-MO-DA HO:MI+ZONE\\n"\n'
            outf.write(po_str if line.startswith(po_str[:20]) else line)


def build_string_template(target, source, env):
    src_files = ' '.join(get_files(['py'], 'feedparser'))
    cmd_tmpl = 'xgettext -d {name} -L python -o {name}.pot '
    system(cmd_tmpl.format(name=env['NAME']) + src_files)
    for lang in env['LANGUAGES']:
        __build_language(env['LANG'], lang, env['NAME'])


def build_strings(target, source, env):
    for lang in env['LANGUAGES']:
        path = env['LANG'] + lang + '/LC_MESSAGES/'
        cmd = 'msgfmt -o {path}{name}.mo {path}{name}.po'
        system(cmd.format(path=path, name=env['NAME']))
