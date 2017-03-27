from yyagl.gameobject import Colleague
from .menu import LoadingMenu, LoadingMenuProps


class LoadingProps(object):

    def __init__(
            self, track_path, car_path, drivers, tracks,
            track_name_transl, single_race, grid, cars_path, drivers_path,
            joystick, keys, menu_args):
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


class Loading(Colleague):

    def __init__(self, mdt):  # otherwise it doesn't work
        self.mdt = mdt

    def enter_loading(self, loading_props):
        l_p = loading_props
        loadingmenu_props = LoadingMenuProps(
            self, l_p.track_path, l_p.car_path, l_p.drivers, l_p.tracks,
            l_p.track_name_transl, l_p.single_race, l_p.grid, l_p.cars_path,
            l_p.drivers_path, l_p.joystick, l_p.keys, l_p.menu_args)
        self.menu = LoadingMenu(loadingmenu_props)

    def exit_loading(self):
        self.menu.destroy()
