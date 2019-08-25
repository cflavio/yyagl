from random import randint
from copy import deepcopy
from yyagl.gameobject import GameObject, GuiColleague
from yyagl.engine.gui.menu import Menu, MenuLogic
from .loadingpage import LoadingPage


class LoadingGui(GuiColleague):

    def __init__(self, mediator, rprops, loading, track_name_transl,
                 drivers, ranking, tuning):
        GuiColleague.__init__(self, mediator)
        pbackground = 'assets/images/loading/%s%s.txo'
        pbackground = pbackground % (rprops.track_name, randint(1, 4))
        menu_props = deepcopy(rprops.season_props.gameprops.menu_props)
        menu_props.background_img_path = pbackground
        self.menu = Menu(menu_props)
        self.menu.loading = loading
        self.menu.push_page(LoadingPage(
            rprops, self.menu, track_name_transl, drivers, ranking, tuning))

    def destroy(self):
        self.menu = self.menu.destroy()
        GuiColleague.destroy(self)


class LoadingMenu(Menu):
    # move to game's code

    def __init__(self, rprops, loading, track_name_transl, drivers, ranking, tuning):
        init_lst = [
            [('gui', LoadingGui, [self, rprops, loading,
                                  track_name_transl, drivers, ranking, tuning])],
            [('logic', MenuLogic, [self])]]
        GameObject.__init__(self, init_lst)  # invoke Menu's __init__

    def destroy(self):
        GameObject.destroy(self)
