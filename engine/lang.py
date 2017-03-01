from gettext import install, translation
from ..gameobject import Colleague


class LangMgr(Colleague):

    def __init__(self, mdt):
        Colleague.__init__(self, mdt)
        self.curr_lang = eng.logic.cfg.lang
        self.set_lang(eng.logic.cfg.lang)

    @property
    def lang_codes(self):
        return [lang[:2].lower() for lang in eng.logic.cfg.languages]

    def set_lang(self, lang):
        self.curr_lang = lang
        cfg = eng.logic.cfg
        try:
            lang = translation(cfg.lang_domain, cfg.lang_path, [lang])
            lang.install(unicode=1)
        except IOError:  # english
            install(cfg.lang_domain, cfg.lang_path, unicode=1)
