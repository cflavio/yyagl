from gettext import install, translation
from ..singleton import Singleton


class LangMgr:
    __metaclass__ = Singleton

    def __init__(self, lang, lang_domain, lang_path):
        self.curr_lang = lang
        self.domain = lang_domain
        self.path = lang_path
        self.set_lang(lang)

    @property
    def lang_codes(self):
        return [lang[:2].lower() for lang in eng.cfg.languages]

    def set_lang(self, lang):
        self.curr_lang = lang
        try:
            translation(self.domain, self.path, [lang]).install(unicode=1)
        except IOError:  # english
            install(self.domain, self.path, unicode=1)
