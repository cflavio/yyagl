from pathlib import Path
import sys
if '' in sys.path: sys.path.remove('')
sys.path.append(str(Path(__file__).parent.parent.parent))
from os import system, remove
from os.path import exists
from unittest import TestCase
from yyagl.dictfile import DctFile


class DictFileTests(TestCase):

    def setUp(self):
        if exists('./tests/test.json'): remove('./tests/test.json')
        self.dctfile = DctFile(
            './tests/test.json',
            {'a': 0, 'b': 1, 'c': 2})
        self.dctfile.store()

    def tearDown(self):
        remove('./tests/test.json')

    def test_init(self):
        self.assertIsNotNone(self.dctfile)

    def test_deepupdate(self):
        self.dctfile['a'] = {'b': {'c': 4}}
        self.assertEqual(self.dctfile['a']['b']['c'], 4)
        self.dctfile['a'] = DctFile.deepupdate(self.dctfile['a'], {'b': {'c': 5}})
        self.assertEqual(self.dctfile['a']['b']['c'], 5)

    def test_store(self):
        self.assertEqual(self.dctfile['c'], 2)
        other = DctFile('./tests/test.json')
        self.dctfile['c'] = 3
        self.assertEqual(self.dctfile['c'], 3)
        self.assertEqual(other['c'], 2)
        self.dctfile.store()
        other = DctFile('./tests/test.json')
        self.assertEqual(other['c'], 3)

    def test_operations(self):
        self.assertEqual(self.dctfile['c'], 2)
        self.dctfile['d'] = 3
        self.assertEqual(self.dctfile['d'], 3)
        self.assertIn('d', self.dctfile.dct)
        del self.dctfile['d']
        self.assertNotIn('d', self.dctfile.dct)
