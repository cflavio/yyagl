from panda3d.core import TextNode, NodePath
from direct.gui.OnscreenText import OnscreenText
from yyagl.gameobject import Colleague
from yyagl.engine.gui.page import PageGui
from direct.gui.DirectGuiGlobals import FLAT
from direct.gui.DirectButton import DirectButton
from .menu import LoadingMenu


class Loading(Colleague):

    def __init__(self, mdt):
        self.mdt = mdt

    def enter_loading(self, track_path='', car_path='', player_cars=[]):
        self.menu = LoadingMenu(self, track_path, car_path, player_cars)

    def exit_loading(self):
        self.menu.destroy()
