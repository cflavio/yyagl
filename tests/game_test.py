from mock import create_autospec
from os import chdir, getcwd
from panda3d.core import loadPrcFileData, NodePath
from unittest import TestCase
from racing.game.engine.engine import Engine
from racing.game.engine.configuration import Cfg
from racing.game.game import GameLogic, Game
from racing.game.gameobject import GameObject, FsmColleague, GfxColleague, PhysColleague, GuiColleague, AudioColleague, \
    AiColleague, EventColleague


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


class GameTests(TestCase):

    def setUp(self):
        loadPrcFileData('', 'window-type none')
        loadPrcFileData('', 'audio-library-name null')

    def test_init(self):
        conf = Cfg()
        classes = [FsmColleague, GfxColleague, PhysColleague, GuiColleague, GameLogic, AudioColleague, AiColleague, EventColleague]
        game = Game(classes, conf)
        self.assertIsInstance(game, Game)
        game.destroy()

    def tearDown(self):
        self.eng.destroy()
