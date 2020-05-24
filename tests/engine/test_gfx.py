from pathlib import Path
import sys
if '' in sys.path: sys.path.remove('')
sys.path.append(str(Path(__file__).parent.parent.parent))
from unittest import TestCase
from panda3d.core import loadPrcFileData
from yyagl.engine.engine import Engine
from yyagl.lib.p3d.gfx import P3dNode


class EngineGfxTests(TestCase):

    def setUp(self):
        loadPrcFileData('', 'window-type none')
        loadPrcFileData('', 'audio-library-name null')
        self.eng = Engine()

    def tearDown(self): self.eng.destroy()

    def test_init_clean(self):
        self.eng.gfx.init()
        self.assertIsInstance(self.eng.gfx.root, P3dNode)
        self.eng.gfx.clean()
        self.assertTrue(self.eng.gfx.root.is_empty)

    def test_frame_rate(self):
        self.eng.gfx.set_frame_rate(60)
