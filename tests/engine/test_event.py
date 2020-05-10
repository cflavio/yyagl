from pathlib import Path
import sys
if '' in sys.path: sys.path.remove('')
sys.path.append(str(Path(__file__).parent.parent.parent))
from unittest import TestCase
from unittest.mock import patch, create_autospec
from panda3d.core import loadPrcFileData, GraphicsWindow
from yyagl.engine.engine import Engine
from yyagl.engine.event import EngineEvent


class EngineEventTests(TestCase):

    def setUp(self):
        loadPrcFileData('', 'window-type none')
        loadPrcFileData('', 'audio-library-name null')
        self.eng = Engine()
        EngineEvent(self.eng, True)

    def tearDown(self): self.eng.destroy()

    def test_init(self): self.assertIsInstance(self.eng.event, EngineEvent)

    def test_key2desc(self):
        with patch('builtins.base') as patched_base:
            # we need to patch it to run without base.win
            self.assertEqual(str(self.eng.event.key2desc('x')), 'x')
            base.win.get_keyboard_map().get_mapped_button_label = create_autospec(GraphicsWindow)
            base.win.get_keyboard_map().get_mapped_button_label.return_value = 'x'
            self.assertEqual(self.eng.event.key2desc('raw-x'), 'x')

    def test_desc2key(self):
        with patch('builtins.base') as patched_base:
            self.assertEqual(self.eng.event.desc2key('x'), 'x')
