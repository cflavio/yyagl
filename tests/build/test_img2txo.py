from pathlib import Path
import sys
if '' in sys.path: sys.path.remove('')
sys.path.append(str(Path(__file__).parent.parent.parent))
from os import system, remove
from os.path import exists
from sys import executable
from unittest import TestCase


class Img2TxoTests(TestCase):

    def setUp(self):
        if exists('./assets/image.txo'): remove('./assets/image.txo')

    def test_img2txo(self):
        system(executable + ' ./build/img2txo.py "./assets/image.png"')
        self.assertTrue(exists('./assets/image.txo'))
