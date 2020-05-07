from pathlib import Path
import sys
if '' in sys.path: sys.path.remove('')
sys.path.append(str(Path(__file__).parent.parent.parent))
from unittest import TestCase
from unittest.mock import MagicMock
from yyagl.observer import Subject


class Observed(Subject): pass


class Observer:

    def __init__(self, observed): self.__observed = observed

    def callback(self): pass


class ObserverTests(TestCase):

    def test_all(self):
        observed = Observed()
        observer = Observer(observed)
        observer.callback = MagicMock(side_effect=observer.callback)
        observer.callback.__name__ = 'callback'
        self.assertFalse(observed.observing(observer.callback))
        observed.attach(observer.callback)
        self.assertTrue(observed.observing(observer.callback))
        observer.callback.assert_not_called()
        observed.notify('callback')
        observer.callback.assert_called()
        observed.detach(observer.callback)
        self.assertFalse(observed.observing(observer.callback))
