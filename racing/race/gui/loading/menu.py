from yyagl.gameobject import GameObject, Gui
from yyagl.engine.gui.menu import Menu, MenuLogic
from .loadingpage import LoadingPage


class LoadingGui(Gui):

    def __init__(self, mdt, rprops, sprops, loading, track_name_transl,
                 drivers):
        Gui.__init__(self, mdt)
        self.menu = Menu(rprops.menu_args)
        self.menu.loading = loading
        self.menu.push_page(LoadingPage(
            rprops, sprops, self.menu, track_name_transl, drivers))

    def destroy(self):
        self.menu = self.menu.destroy()
        Gui.destroy(self)


class LoadingMenu(Menu):
    # move to game's code

    def __init__(self, rprops, sprops, loading, track_name_transl, drivers):
        init_lst = [
            [('gui', LoadingGui, [self, rprops, sprops, loading,
                                  track_name_transl, drivers])],
            [('logic', MenuLogic, [self])]]
        GameObject.__init__(self, init_lst)  # NB doesn't invoke Menu's
