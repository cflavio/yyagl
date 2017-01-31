from yyagl.gameobject import Gui
from .results import Results
from .loading.loading import Loading


class RaceGui(Gui):

    def __init__(self, mdt):
        Gui.__init__(self, mdt)
        self.results = Results()
        self.loading = Loading(mdt)

    def destroy(self):
        Gui.destroy(self)
        self.results.destroy()
        self.loading.destroy()
