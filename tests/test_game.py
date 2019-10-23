from unittest.mock import create_autospec
from os import chdir, getcwd
from panda3d.core import loadPrcFileData, NodePath
from unittest import TestCase
from yyagl.engine.engine import Engine
from yyagl.engine.configuration import Cfg
from yyagl.game import GameLogic, Game
from yyagl.gameobject import GameObject, FsmColleague, GfxColleague, PhysColleague, GuiColleague, AudioColleague, \
    AiColleague, EventColleague, LogicColleague


class LogicTests(TestCase):

    def setUp(self):
        loadPrcFileData('', 'window-type none')
        loadPrcFileData('', 'audio-library-name null')

    def tearDown(self):
        self.eng.destroy()

    def test_init(self):
        self.eng = Engine()
        game_obj = GameObject()
        logic = GameLogic(game_obj)
        self.assertIsInstance(logic, GameLogic)


class GameInstance(Game):

    def __init__(self):
        conf = Cfg()
        init_lst = [
            [('fsm', FsmColleague, [self])],
            [('logic', LogicColleague, [self])],
            [('audio', AudioColleague, [self])],
            [('event', EventColleague, [self])]]
        Game.__init__(self, init_lst, conf)

class GameTests(TestCase):

    def setUp(self):
        loadPrcFileData('', 'window-type none')
        loadPrcFileData('', 'audio-library-name null')

    def test_init(self):
        self.game = GameInstance()
        self.assertIsInstance(self.game, Game)
        self.game.destroy()

    def tearDown(self):
        self.game.eng.destroy()
