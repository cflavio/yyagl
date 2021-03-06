from pathlib import Path
import sys
if '' in sys.path: sys.path.remove('')
sys.path.append(str(Path(__file__).parent.parent.parent))
from unittest.mock import patch
from unittest import TestCase
from panda3d.core import loadPrcFileData
from yyagl.engine.engine import Engine
from yyagl.gameobject import AiColleague, AudioColleague, EventColleague, \
    FsmColleague, GameObject, GfxColleague, GuiColleague, LogicColleague, \
    PhysColleague, Colleague


class AiTests(TestCase):

    def setUp(self):
        loadPrcFileData('', 'window-type none')
        loadPrcFileData('', 'audio-library-name null')

    def tearDown(self):
        self.engine.destroy()

    def test_init(self):
        self.engine = Engine()
        game_obj = GameObject()
        ai = AiColleague(game_obj)
        self.assertIsInstance(ai, AiColleague)


class AudioTests(TestCase):

    def setUp(self):
        loadPrcFileData('', 'window-type none')
        loadPrcFileData('', 'audio-library-name null')

    def tearDown(self):
        self.engine.destroy()

    def test_init(self):
        self.engine = Engine()
        game_obj = GameObject()
        audio = AudioColleague(game_obj)
        self.assertIsInstance(audio, AudioColleague)


class ColleagueTests(TestCase):

    def setUp(self):
        loadPrcFileData('', 'window-type none')
        loadPrcFileData('', 'audio-library-name null')

    def tearDown(self):
        self.engine.destroy()

    def test_init(self):
        self.engine = Engine()
        game_obj = GameObject()
        colleague = Colleague(game_obj)
        self.assertIsInstance(colleague, Colleague)


class EventTests(TestCase):

    def setUp(self):
        loadPrcFileData('', 'window-type none')
        loadPrcFileData('', 'audio-library-name null')

    def tearDown(self):
        self.engine.destroy()

    def test_init(self):
        self.engine = Engine()
        game_obj = GameObject()
        event = EventColleague(game_obj)
        self.assertIsInstance(event, EventColleague)


class FsmTests(TestCase):

    def setUp(self):
        loadPrcFileData('', 'window-type none')
        loadPrcFileData('', 'audio-library-name null')

    def tearDown(self):
        self.engine.destroy()

    def test_init(self):
        self.engine = Engine()
        game_obj = GameObject()
        fsm = FsmColleague(game_obj)
        self.assertIsInstance(fsm, FsmColleague)


class GfxTests(TestCase):

    def setUp(self):
        loadPrcFileData('', 'window-type none')
        loadPrcFileData('', 'audio-library-name null')

    def tearDown(self):
        self.engine.destroy()

    def test_init(self):
        self.engine = Engine()
        game_obj = GameObject()
        gfx = GfxColleague(game_obj)
        self.assertIsInstance(gfx, GfxColleague)


class GuiTests(TestCase):

    def setUp(self):
        loadPrcFileData('', 'window-type none')
        loadPrcFileData('', 'audio-library-name null')

    def tearDown(self):
        self.engine.destroy()

    def test_init(self):
        self.engine = Engine()
        game_obj = GameObject()
        gui = GuiColleague(game_obj)
        self.assertIsInstance(gui, GuiColleague)


class LogicTests(TestCase):

    def setUp(self):
        loadPrcFileData('', 'window-type none')
        loadPrcFileData('', 'audio-library-name null')

    def tearDown(self):
        self.engine.destroy()

    def test_init(self):
        self.engine = Engine()
        game_obj = GameObject()
        logic = LogicColleague(game_obj)
        self.assertIsInstance(logic, LogicColleague)


class PhysicsTests(TestCase):

    def setUp(self):
        loadPrcFileData('', 'window-type none')
        loadPrcFileData('', 'audio-library-name null')

    def tearDown(self):
        self.engine.destroy()

    def test_init(self):
        self.engine = Engine()
        game_obj = GameObject()
        phys = PhysColleague(game_obj)
        self.assertIsInstance(phys, PhysColleague)


class GameObjectInstance(GameObject):

    def __init__(self):
        GameObject.__init__(self)
        self.fsm = FsmColleague(self)
        self.event = EventColleague(self)
        self.ai = AiColleague(self)
        self.phys = PhysColleague(self)
        self.audio = AudioColleague(self)
        self.logic = LogicColleague(self)
        self.gui = GuiColleague(self)
        self.gfx = GfxColleague(self)

    def destroy(self):
        self.fsm.destroy()
        self.event.destroy()
        self.ai.destroy()
        self.phys.destroy()
        self.audio.destroy()
        self.logic.destroy()
        self.gui.destroy()
        self.gfx.destroy()


class GameObjectTests(TestCase):

    def setUp(self):
        loadPrcFileData('', 'window-type none')
        loadPrcFileData('', 'audio-library-name null')

    def tearDown(self):
        self.engine.destroy()

    @patch.object(GfxColleague, 'destroy')
    @patch.object(GuiColleague, 'destroy')
    @patch.object(LogicColleague, 'destroy')
    @patch.object(AudioColleague, 'destroy')
    @patch.object(PhysColleague, 'destroy')
    @patch.object(AiColleague, 'destroy')
    @patch.object(EventColleague, 'destroy')
    @patch.object(FsmColleague, 'destroy')
    def test_init(
            self, mock_fsm_destroy, mock_event_destroy, mock_ai_destroy,
            mock_phys_destroy, mock_audio_destroy, mock_logic_destroy,
            mock_gui_destroy, mock_gfx_destroy):
        self.engine = Engine()
        mock_event_destroy.__name__ = 'destroy'
        game_obj = GameObjectInstance()
        self.assertIsInstance(game_obj, GameObject)
        game_obj.destroy()
        assert mock_fsm_destroy.called
        assert mock_event_destroy.called
        assert mock_ai_destroy.called
        assert mock_phys_destroy.called
        assert mock_audio_destroy.called
        assert mock_logic_destroy.called
        assert mock_gui_destroy.called
        assert mock_gfx_destroy.called
