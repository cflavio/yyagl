from yyagl.gameobject import Colleague
from .menu import LoadingMenu


class Loading(Colleague):

    def __init__(self, mdt):
        self.mdt = mdt

    def enter_loading(self, track_path='', car_path='', player_cars=[],
                      drivers=None):
        args = (self, track_path, car_path, player_cars, drivers)
        self.menu = LoadingMenu(*args)

    def exit_loading(self):
        self.menu.destroy()
