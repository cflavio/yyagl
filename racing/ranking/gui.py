from direct.gui.OnscreenText import OnscreenText
from direct.gui.OnscreenImage import OnscreenImage
from yyagl.gameobject import Gui


class RankingGui(Gui):

    def __init__(self, mdt, background, font, fg_col):
        Gui.__init__(self, mdt)
        self.ranking_texts = []
        self.background_path = background
        self.font = font
        self.fg_col = fg_col
        self.background = None

    def show(self):
        self.background = OnscreenImage(
            self.background_path, scale=(1.77778, 1, 1.0))
        self.background.setBin('background', 10)
        items = self.mdt.logic.ranking.items()
        sorted_ranking = reversed(sorted(items, key=lambda el: el[1]))
        font = eng.load_font(self.font)
        self.ranking_texts = []
        for i, (name, score) in enumerate(sorted_ranking):
            txt = OnscreenText(
                '%s %s' % (name, score), pos=(0, .5 - .2 * i), font=font,
                fg=self.fg_col, scale=.12)
            self.ranking_texts += [txt]

    def hide(self):
        map(lambda wdg: wdg.destroy(), self.ranking_texts + [self.background])

    def destroy(self):
        self.ranking_texts = None
        Gui.destroy(self)
