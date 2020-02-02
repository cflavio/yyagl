from unittest.mock import patch, create_autospec
from panda3d.core import loadPrcFileData
from unittest import TestCase
from yyagl.gameobject import GameObject
from yyagl.engine.engine import Engine
from yyagl.computer_proxy import ComputerProxy, compute_once, once_a_frame


class ExampleProxy(GameObject, ComputerProxy):

    def __init__(self):
        GameObject.__init__(self)
        ComputerProxy.__init__(self)
        self.reset()

    def reset(self): self.cnt = 0

    @compute_once
    def inc_cnt(self): self.cnt += 1

    @once_a_frame
    def inc_cnt_frame(self): self.cnt += 1


class ComputerProxyTests(TestCase):

    def setUp(self):
        loadPrcFileData('', 'window-type none')
        loadPrcFileData('', 'audio-library-name null')
        self.engine = Engine()
        self.example_proxy = ExampleProxy()

    def tearDown(self):
        self.engine.destroy()

    def test_init(self):
        self.assertIsInstance(self.example_proxy, ExampleProxy)

    def test_compute_once(self):
        self.example_proxy.reset()
        self.example_proxy.inc_cnt()
        self.example_proxy.inc_cnt()
        self.assertEqual(self.example_proxy.cnt, 1)

    def test_compute_once_a_frame(self):
        self.example_proxy.reset()
        self.example_proxy.on_start_frame()
        self.example_proxy.inc_cnt_frame()
        self.example_proxy.inc_cnt_frame()
        self.assertEqual(self.example_proxy.cnt, 1)
        self.example_proxy.on_start_frame()
        self.example_proxy.inc_cnt_frame()
        self.example_proxy.inc_cnt_frame()
        self.assertEqual(self.example_proxy.cnt, 2)
