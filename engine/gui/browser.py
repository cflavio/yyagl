from sys import platform
from os import environ, system
from webbrowser import open_new_tab


class BrowserStrategy(object):

    @staticmethod
    def open(url): open_new_tab(url)


class BrowserStrategyLinux(BrowserStrategy):

    @staticmethod
    def open(url):
        environ['LD_LIBRARY_PATH'] = ''
        system('xdg-open ' + url)


class Browser(object):

    @staticmethod
    def open(url):
        cls = BrowserStrategyLinux if platform.startswith('linux') else \
            BrowserStrategy
        cls.open(url)
