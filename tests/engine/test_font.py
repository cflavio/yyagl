from pathlib import Path
import sys
if '' in sys.path: sys.path.remove('')
sys.path.append(str(Path(__file__).parent.parent.parent))
from unittest import TestCase
from panda3d.core import loadPrcFileData, DynamicTextFont
from yyagl.engine.engine import Engine


class EngineFontTests(TestCase):

    def setUp(self):
        loadPrcFileData('', 'window-type none')
        loadPrcFileData('', 'audio-library-name null')
        self.eng = Engine()

    def tearDown(self): self.eng.destroy()

    def test_font(self):
        font = self.eng.font_mgr.load_font('../assets/fonts/Hanken-Book.ttf')
        print(font)
        self.assertIsInstance(font, DynamicTextFont)
