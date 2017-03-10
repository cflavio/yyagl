from yyagl.gameobject import GameObjectMdt, Gui
from yyagl.engine.gui.menu import Menu, MenuLogic
from .loadingpage import LoadingPage


class LoadingGui(Gui):

    def __init__(
            self, mdt, loading, track_path, car_path, drivers, tracks,
            track_name_transl, single_race, grid, cars_path, drivers_path,
            joystick, keys, menu_args):
        Gui.__init__(self, mdt)
        self.menu = Menu(menu_args)
        self.menu.loading = loading
        self.menu.logic.push_page(LoadingPage(
            self.menu, track_path, car_path, drivers, tracks,
            track_name_transl, single_race, grid, cars_path, drivers_path,
            joystick, keys))

    def destroy(self):
        Gui.destroy(self)
        self.menu = self.menu.destroy()


class LoadingMenu(Menu):
    # move to the game level

    def __init__(
            self, loading, track_path, car_path, drivers, tracks,
            track_name_transl, single_race, grid, cars_path, drivers_path,
            joystick, keys, menu_args):
        init_lst = [
            [('gui', LoadingGui, [
                self, loading, track_path, car_path, drivers, tracks,
                track_name_transl, single_race, grid, cars_path, drivers_path,
                joystick, keys, menu_args])],
            [('logic', MenuLogic, [self])]]
        GameObjectMdt.__init__(self, init_lst)  # NB doesn't invoke Menu's
