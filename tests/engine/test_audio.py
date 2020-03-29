from pathlib import Path
import sys
if '' in sys.path: sys.path.remove('')
sys.path.append(str(Path(__file__).parent.parent.parent))
from unittest import TestCase
from panda3d.core import loadPrcFileData
from yyagl.engine.engine import Engine
from yyagl.engine.audio import EngineAudio


class EngineAudioTests(TestCase):

    def setUp(self):
        loadPrcFileData('', 'window-type none')
        #loadPrcFileData('', 'audio-library-name null')
        self.eng = Engine()
        EngineAudio(self.eng, .4)

    def tearDown(self): self.eng.destroy()

    def test_init(self): self.assertIsInstance(self.eng.audio, EngineAudio)

    def test_volume(self):
        self.assertAlmostEqual(self.eng.lib.volume, .4)
        self.eng.audio.set_volume(.2)
        self.assertAlmostEqual(self.eng.lib.volume, .2)
