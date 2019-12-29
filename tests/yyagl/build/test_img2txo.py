from os import system, remove
from os.path import exists
from sys import executable
from unittest import TestCase


class Img2TxoTests(TestCase):

    def setUp(self):
        if exists('./yyagl/assets/image.txo'): remove('./yyagl/assets/image.txo')

    def test_img2txo(self):
        system(executable + ' ./yyagl/build/img2txo.py "./yyagl/assets/image.png"')
        self.assertTrue(exists('./yyagl/assets/image.txo'))
