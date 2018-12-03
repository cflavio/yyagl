from panda3d.core import TextNode
from direct.gui.OnscreenText import OnscreenText
from direct.gui.OnscreenImage import OnscreenImage
from yyagl.gameobject import GuiColleague
from yyagl.facade import Facade
from .results import Results, ResultsServer
from .loading.loading import Loading
from .minimap import Minimap


class RaceGuiFacade(Facade):

    def __init__(self):
        Facade.__init__(self, mth_lst=[('update_minimap', lambda obj: obj.minimap.update)])


class RaceGui(GuiColleague, RaceGuiFacade):

    result_cls = Results

    def __init__(self, mediator, rprops):
        GuiColleague.__init__(self, mediator)
        r_p = self.props = rprops
        self.results = self.result_cls(rprops)
        self.loading = Loading()
        self.minimap = None
        RaceGuiFacade.__init__(self)

    def start(self):
        self.minimap = Minimap(
            self.mediator.track.bounds, self.props.minimap_path,
            self.props.minimap_image, self.props.col_dct,
            self.props.season_props.car_names,
            self.props.season_props.player_car_name)

    def destroy(self):
        self.results.destroy()
        if self.minimap: self.minimap.destroy()  # e.g. server has quit on loading
        GuiColleague.destroy(self)


class RaceGuiServer(RaceGui):

    result_cls = ResultsServer
