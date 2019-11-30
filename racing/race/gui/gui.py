from panda3d.core import TextNode
from direct.gui.OnscreenText import OnscreenText
from direct.gui.OnscreenImage import OnscreenImage
from yyagl.gameobject import GuiColleague
from yyagl.facade import Facade
from yyagl.racing.player.player import Player
from .results import Results, ResultsServer
from .loading.loading import Loading
from .minimap import Minimap


class RaceGuiFacade(Facade):

    def __init__(self):
        Facade.__init__(self, mth_lst=[('update_minimap', lambda obj: obj.minimap.update)])


class RaceGui(GuiColleague, RaceGuiFacade):

    result_cls = Results

    def __init__(self, mediator, rprops, players):
        GuiColleague.__init__(self, mediator)
        self._players = players
        r_p = self.props = rprops
        self.results = self.result_cls(rprops)
        self.loading = Loading()
        self.minimap = None
        RaceGuiFacade.__init__(self)

    def start(self):
        car_names = [player.car for player in self._players]
        player_car_name = [player.car for player in self._players if player.kind == Player.human]
        self.minimap = Minimap(
            self.mediator.track.bounds, self.props.minimap_path,
            self.props.minimap_image, self.props.col_dct,
            car_names, player_car_name)

    def destroy(self):
        self.results.destroy()
        if self.minimap: self.minimap.destroy()  # e.g. server has quit on loading
        GuiColleague.destroy(self)


class RaceGuiServer(RaceGui):

    result_cls = ResultsServer
