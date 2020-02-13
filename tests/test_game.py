from pathlib import Path
import sys
if '' in sys.path: sys.path.remove('')
sys.path.append(str(Path(__file__).parent.parent.parent))
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
        Game.__init__(self, conf)
        self.fsm = FsmColleague(self)
        self.logic = LogicColleague(self)
        self.audio = AudioColleague(self)
        self.event = EventColleague(self)

    def destroy(self):
        self.fsm.destroy()
        self.logic.destroy()
        self.audio.destroy()
        self.event.destroy()


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
