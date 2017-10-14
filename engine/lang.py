from os.path import join
from gettext import install, translation
from yyagl.gameobject import GameObject


class LangMgr(GameObject):

    def __init__(self, lang, domain, dpath):
        GameObject.__init__(self)
        self.lang = lang
        self.domain = domain
        self.dpath = join(self.eng.curr_path, dpath)
        self.set_lang(lang)

    @property
    def lang_codes(self):
        return [lang[:2].lower() for lang in self.eng.cfg.lang_cfg.languages]

    def set_lang(self, lang):
        self.lang = lang
        try:
            translation(self.domain, self.dpath, [lang]).install(unicode=1)
        except IOError:  # english translation is already in the code
            install(self.domain, self.dpath, unicode=1)
