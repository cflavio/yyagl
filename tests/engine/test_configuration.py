from pathlib import Path
import sys
if '' in sys.path: sys.path.remove('')
sys.path.append(str(Path(__file__).parent.parent.parent))
from unittest import TestCase
from unittest.mock import MagicMock
from panda3d.core import loadPrcFileData, ConfigVariableInt, ConfigVariableString
from yyagl.engine.engine import Engine
from yyagl.engine.configuration import Cfg


class EngineConfigurationTests(TestCase):

    def setUp(self):
        loadPrcFileData('', 'window-type none')
        loadPrcFileData('', 'audio-library-name null')
        self.eng = Engine()

    def tearDown(self):
        self.eng.destroy()

    def test_cfg(self):
        # let's check some fields
        self.assertEqual(self.eng.cfg.gui_cfg.fps, False)
        self.assertEqual(self.eng.cfg.profiling_cfg.profiling, False)
        self.assertEqual(self.eng.cfg.lang_cfg.lang, 'en')
        self.assertEqual(self.eng.cfg.cursor_cfg.cursor_hidden, False)
        self.assertEqual(self.eng.cfg.dev_cfg.multithreaded_render, False)

    def test_cfg_configure(self):
        # let's check that __configure has been executed
        self.assertEqual(ConfigVariableInt('texture-anosotropic-degree').getValue(), 2)
