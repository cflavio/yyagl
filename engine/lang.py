from logging import info
from os.path import join
from gettext import translation
from yyagl.gameobject import GameObject


class LangMgr(GameObject):

    def __init__(self, lang, domain, dpath):
        GameObject.__init__(self)
        self.lang = lang
        self.domain = domain
        self.dpath = join(self.eng.curr_path, dpath)
        info('language: %s, %s' % (self.domain, self.dpath))
        self.set_lang(lang)

    @property
    def lang_codes(self):
        return [lang[1] for lang in self.eng.cfg.lang_cfg.languages]

    def set_lang(self, lang):
        self.lang = lang
        args = lang, self.domain, self.dpath
        info('setting language %s, %s, %s' % args)
        tra = translation(self.domain, self.dpath, [lang], fallback=True)
        tra.install()
