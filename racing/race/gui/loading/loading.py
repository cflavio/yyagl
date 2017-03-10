from yyagl.gameobject import Colleague
from .menu import LoadingMenu


class Loading(Colleague):

    def __init__(self, mdt):  # otherwise it doesn't work
        self.mdt = mdt

    def enter_loading(
            self, track_path, car_path, drivers, tracks, track_name_transl,
            single_race, grid, cars_path, drivers_path, joystick, keys,
            menu_args):
        args = (
            self, track_path, car_path, drivers, tracks, track_name_transl,
            single_race, grid, cars_path, drivers_path, joystick, keys,
            menu_args)
        self.menu = LoadingMenu(*args)

    def exit_loading(self):
        self.menu.destroy()
