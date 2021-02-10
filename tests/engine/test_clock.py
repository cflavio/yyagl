from pathlib import Path
import sys
if '' in sys.path: sys.path.remove('')
sys.path.append(str(Path(__file__).parent.parent.parent))
from unittest import TestCase
from unittest.mock import MagicMock
from panda3d.core import loadPrcFileData
from yyagl.engine.engine import Engine
from yyagl.engine.audio import EngineAudio


class EngineClockTests(TestCase):

    def setUp(self):
        loadPrcFileData('', 'window-type none')
        loadPrcFileData('', 'audio-library-name null')
        self.eng = Engine()

    def tearDown(self):
        self.eng.destroy()

    def test_clock(self):
        # this test shows that even if you process frames, the engine's clock
        # is storing the unpaused time
        start_time = self.eng.clock.time
        self.eng.pause.logic.pause()
        taskMgr.step()
        self.eng.pause.logic.resume()
        self.assertEqual(start_time, self.eng.clock.time)
