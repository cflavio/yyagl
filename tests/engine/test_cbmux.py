from pathlib import Path
import sys
if '' in sys.path: sys.path.remove('')
sys.path.append(str(Path(__file__).parent.parent.parent))
from unittest import TestCase
from unittest.mock import MagicMock
from panda3d.core import loadPrcFileData
from yyagl.engine.engine import Engine


class EngineCBMuxTests(TestCase):

    def setUp(self):
        loadPrcFileData('', 'window-type none')
        loadPrcFileData('', 'audio-library-name null')
        self.eng = Engine()

    def tearDown(self):
        self.eng.destroy()

    def _callback(self, arg): pass

    def test_cbmux(self):
        self._callback = MagicMock(side_effect=self._callback)
        self.eng.cb_mux.add_cb(self._callback, [42])
        taskMgr.step()
        self._callback.assert_called_with(42)
