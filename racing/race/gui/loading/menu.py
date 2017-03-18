from yyagl.gameobject import GameObjectMdt, Gui
from yyagl.engine.gui.menu import Menu, MenuLogic
from .loadingpage import LoadingPage, LoadingPageProps


class LoadingGuiProps(object):

    def __init__(
            self, loading, track_path, car_path, drivers, tracks,
            track_name_transl, single_race, grid, cars_path, drivers_path,
            joystick, keys, menu_args):
        self.loading = loading
        self.track_path = track_path
        self.car_path = car_path
        self.drivers = drivers
        self.tracks = tracks
        self.track_name_transl = track_name_transl
        self.single_race = single_race
        self.grid = grid
        self.cars_path = cars_path
        self.drivers_path = drivers_path
        self.joystick = joystick
        self.keys = keys
        self.menu_args = menu_args


class LoadingGui(Gui):

    def __init__(self, mdt, loadinggui_props):
        Gui.__init__(self, mdt)
        l_p = loadinggui_props
        self.menu = Menu(l_p.menu_args)
        self.menu.loading = l_p.loading
        loadingpage_props = LoadingPageProps(
            self.menu, l_p.track_path, l_p.car_path, l_p.drivers, l_p.tracks,
            l_p.track_name_transl, l_p.single_race, l_p.grid, l_p.cars_path,
            l_p.drivers_path, l_p.joystick, l_p.keys)
        self.menu.push_page(LoadingPage(loadingpage_props))

    def destroy(self):
        self.menu = self.menu.destroy()
        Gui.destroy(self)


class LoadingMenuProps(object):

    def __init__(
            self, loading, track_path, car_path, drivers, tracks,
            track_name_transl, single_race, grid, cars_path, drivers_path,
            joystick, keys, menu_args):
         self.loading = loading
         self.track_path = track_path
         self.car_path = car_path
         self.drivers = drivers
         self.tracks = tracks
         self.track_name_transl = track_name_transl
         self.single_race = single_race
         self.grid = grid
         self.cars_path = cars_path
         self.drivers_path = drivers_path
         self.joystick = joystick
         self.keys = keys
         self.menu_args = menu_args


class LoadingMenu(Menu):
    # move to the game level

    def __init__(self, loadingmenu_props):
        l_p = loadingmenu_props
        loadinggui_props = LoadingGuiProps(
            l_p.loading, l_p.track_path, l_p.car_path, l_p.drivers, l_p.tracks,
            l_p.track_name_transl, l_p.single_race, l_p.grid, l_p.cars_path,
            l_p.drivers_path, l_p.joystick, l_p.keys, l_p.menu_args)
        init_lst = [
            [('gui', LoadingGui, [self, loadinggui_props])],
            [('logic', MenuLogic, [self])]]
        GameObjectMdt.__init__(self, init_lst)  # NB doesn't invoke Menu's
