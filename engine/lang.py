from os.path import join
from gettext import install, translation
from yyagl.gameobject import GameObject


class LangMgr(GameObject):

    def __init__(self, lang, lang_domain, lang_path):
        GameObject.__init__(self)
        self.curr_lang = lang
        self.domain = lang_domain
        self.path = join(self.eng.curr_path, lang_path)
        self.set_lang(lang)

    @property
    def lang_codes(self):
        return [lang[:2].lower() for lang in self.eng.cfg.languages]

    def set_lang(self, lang):
        self.curr_lang = lang
        try:
            translation(self.domain, self.path, [lang]).install(unicode=1)
        except IOError:  # english
            install(self.domain, self.path, unicode=1)
