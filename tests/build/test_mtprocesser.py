from os import system, remove
from os.path import exists
from sys import executable
from unittest import TestCase
from yyagl.build.mtprocesser import MultithreadedProcesser


class MtProcesserTests(TestCase):

    def setUp(self):
        for fn_idx in ['1', '2']:
            _fn = './yyagl/tests/%s.txt' % fn_idx
            if exists(_fn): remove(_fn)

    def tearDown(self): self.setUp()

    def test_threaded(self):
        mp_mgr = MultithreadedProcesser(2)
        mp_mgr.add('echo 1 > ./yyagl/tests/1.txt')
        mp_mgr.add('echo 2 > ./yyagl/tests/2.txt')
        mp_mgr.run()
        self.assertTrue(exists('./yyagl/tests/1.txt'))
        self.assertTrue(exists('./yyagl/tests/2.txt'))

    def test_nothreaded(self):
        mp_mgr = MultithreadedProcesser(1)
        mp_mgr.add('echo 1 > ./yyagl/tests/1.txt')
        mp_mgr.run()
        self.assertTrue(exists('./yyagl/tests/1.txt'))
