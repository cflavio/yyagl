from unittest import TestCase
from unittest.mock import MagicMock
from yyagl.observer import Subject


class Observed(Subject): pass


class Observer:

    def __init__(self, observed): self.__observed = observed

    def cb(self): pass


class ObserverTests(TestCase):

    def test_all(self):
        observed = Observed()
        observer = Observer(observed)
        observer.cb = MagicMock(side_effect=observer.cb)
        observer.cb.__name__ = 'cb'
        self.assertFalse(observed.observing(observer.cb))
        observed.attach(observer.cb)
        self.assertTrue(observed.observing(observer.cb))
        observer.cb.assert_not_called()
        observed.notify('cb')
        observer.cb.assert_called()
        observed.detach(observer.cb)
        self.assertFalse(observed.observing(observer.cb))
